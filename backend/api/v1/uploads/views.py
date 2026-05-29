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
from uploads.tasks import process_file_checksum

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

        process_file_checksum.delay(file_instance.id)

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
            # Now it doesn't matter if the browser sends:
            # ?action=DOWNLOAD, ?Action=Download, or ?download=TRUE
            response = FileResponse(file_obj.file.open(), as_attachment=True)
            response["Content-Disposition"] = (
                f'attachment; filename="{file_obj.original_filename}"'
            )
            return response
        # otherwise, just return the file metadata
        serializer = FileSerializer(file_obj)
        return Response(serializer.data)

    # --- HANDLE DELETE
    if request.method == "DELETE":
        # Check if any projects are using this file
        # 'projects' is the related_name we should have in our File model's ManyToMany
        if file_obj.projects.exists():
            return Response(
                {
                    "error": "Locked",
                    "message": f"Cannot delete '{file_obj.original_filename}': It is being used by one or more projects.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_obj.delete()
        return Response(
            {"message": "File deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )


# get all files for a user (admin can see all, regular users see only theirs)
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def files_list(request):
    # If we are here, the user is definitely logged in.
    if request.user.is_superuser:
        files = File.objects.all()
    else:
        files = File.objects.filter(user=request.user)

    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)


# get all file stats(admin can see all, regular users see only theirs)
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def upload_stats(request):
    if request.user.is_superuser:
        files = File.objects.all()
    else:
        files = File.objects.filter(user=request.user)

    # Your ORM logic - nice and efficient
    stats = files.aggregate(total_files=Count("id"), total_size=Sum("file_size"))

    total_bytes = stats["total_size"] or 0

    # Let's give React some helpful pre-calculated numbers
    return Response(
        {
            "total_files": stats["total_files"],
            "storage_used_bytes": total_bytes,
            "storage_used_gb": round(total_bytes / (1024**3), 2),
            "storage_used_mb": round(total_bytes / (1024**2), 2),
        }
    )
