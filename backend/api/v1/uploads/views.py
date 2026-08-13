from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import FileSerializer

from uploads.tasks import celery_upload_file_md5
from uploads.services import delete_file, stream_file
from uploads.models import File

from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum


class Upload(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 1. Validate incoming data
            serializer = FileSerializer(data=request.data, context={"request": request})

            # Returns 400 Bad Request with field errors if input is bad
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 2. Save and trigger task
            file_instance = serializer.save()
            try:
                celery_upload_file_md5.delay(file_instance.id)
            except Exception as task_err:
                # Log the warning without breaking the HTTP request
                print(f"[WARNING] Task dispatch failed: {task_err}")

            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        except (APIException, Http404):
            # Let DRF handle standard HTTP errors (400, 401, 403, 404)
            raise

        except Exception:
            return Response(
                {"error": "An error occurred while uploading the file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilesList(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            files = (
                File.objects.all()
                if request.user.is_superuser
                else File.objects.filter(user=request.user)
            )
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (APIException, Http404):
            # Let DRF handle standard HTTP errors (400, 401, 403, 404)
            raise
        except Exception:
            return Response(
                {"error": "An error occurred while fetching files."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileStats(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            files = (
                File.objects.all()
                if request.user.is_superuser
                else File.objects.filter(user=request.user)
            )
            stats = files.aggregate(
                total_files=Count("id"), total_size=Sum("file_size")
            )
            total_bytes = stats["total_size"] or 0

            return Response(
                {
                    "total_files": stats["total_files"],
                    "storage_used_bytes": total_bytes,
                    "storage_used_gb": round(total_bytes / (1024**3), 2),
                    "storage_used_mb": round(total_bytes / (1024**2), 2),
                },
                status=status.HTTP_200_OK,
            )
        except (APIException, Http404):
            # Let DRF handle standard HTTP errors (400, 401, 403, 404)
            raise
        except Exception:
            return Response(
                {"error": "An error occurred while calculating file stats."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileDownload(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, upload_id):
        try:
            file_obj = get_object_or_404(File, upload_id=upload_id)

            if file_obj.user != request.user and not request.user.is_superuser:
                raise PermissionDenied(
                    "You do not have permission to download this file."
                )

            file_handle = stream_file(file_obj)
            response = FileResponse(file_handle, as_attachment=True)
            response["Content-Disposition"] = (
                f'attachment; filename="{file_obj.original_filename}"'
            )
            return response

        except (APIException, Http404):
            raise
        except Exception:
            return Response(
                {"error": "An unexpected server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileDetail(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # Shared helper: gets object or raises standard DRF HTTP exceptions automatically
    def get_object(self, request, upload_id):
        # 1. If missing, raises Http404 -> DRF turns it into HTTP 404 Not Found automatically
        file_obj = get_object_or_404(File, upload_id=upload_id)

        # 2. If wrong user, raise PermissionDenied -> DRF turns it into HTTP 403 Forbidden automatically
        if file_obj.user != request.user and not request.user.is_superuser:
            raise PermissionDenied(
                "You do not have permission to access or delete this file."
            )

        return file_obj

    def get(self, request, upload_id):
        try:
            file_obj = self.get_object(request, upload_id)
            serializer = FileSerializer(file_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (APIException, Http404):
            raise
        except Exception:
            return Response(
                {"error": "An unexpected server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, upload_id):
        try:
            file_obj = self.get_object(request, upload_id)

            if file_obj.timepoint_runs.exists():
                return Response(
                    {
                        "error": "Locked",
                        "message": f"Cannot delete '{file_obj.original_filename}': It is being used by one or more projects.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            delete_file(file_obj)
            return Response(
                {"message": "File deleted successfully."}, status=status.HTTP_200_OK
            )

        except (APIException, Http404):
            raise
        except ValidationError as e:
            return Response(
                {"error": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"error": "An unexpected server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
