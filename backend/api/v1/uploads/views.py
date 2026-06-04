from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import FileSerializer
from uploads.models import File
from uploads.tasks import process_file_pipeline_task
from uploads.services import delete_file, stream_file

from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.http import FileResponse


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def upload(request):
    serializer = FileSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        file_instance = serializer.save()

        process_file_pipeline_task.delay(file_instance.id)

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def file_detail(request, upload_id):
    # 1. Find the file (or 404 if it doesn't exist)
    file_obj = get_object_or_404(File, upload_id=upload_id)

    # 2. Permission Check: Only owner or superuser
    if file_obj.user != request.user and not request.user.is_superuser:
        return Response(
            {"detail": "You do not have permission to access this file."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # --- HANDLE GET FOR DOWNLOAD OR METADATA
    if request.method == "GET":
        # 1. Get the value. If it's missing, default to an empty string.
        # 2. Force it to lowercase immediately.
        action = request.query_params.get("action", "").lower()
        download_flag = request.query_params.get("download", "").lower()

        if action == "download" or download_flag == "true":
            file_handle = stream_file(file_obj)
            response = FileResponse(file_handle, as_attachment=True)
            response["Content-Disposition"] = (
                f'attachment; filename="{file_obj.original_filename}"'
            )
            return response
        return Response(FileSerializer(file_obj).data)

    if request.method == "DELETE":
        if file_obj.projects.exists():
            return Response(
                {
                    "error": "Locked",
                    "message": f"Cannot delete '{file_obj.original_filename}': It is being used by one or more projects.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delete_file(file_obj)
        return Response(
            {"message": "File deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def files_list(request):
    files = File.objects.all() if request.user.is_superuser else File.objects.filter(user=request.user)
    return Response(FileSerializer(files, many=True).data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def upload_stats(request):
    files = File.objects.all() if request.user.is_superuser else File.objects.filter(user=request.user)
    stats = files.aggregate(total_files=Count("id"), total_size=Sum("file_size"))
    total_bytes = stats["total_size"] or 0
    return Response(
        {
            "total_files": stats["total_files"],
            "storage_used_bytes": total_bytes,
            "storage_used_gb": round(total_bytes / (1024**3), 2),
            "storage_used_mb": round(total_bytes / (1024**2), 2),
        }
    )
