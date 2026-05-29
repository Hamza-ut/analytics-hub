from rest_framework import serializers

from uploads.models import File
from uploads.utils import validate_file


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "upload_id",
            "file",
            "original_filename",
            "file_size",
            "status",
            "md5",
        ]
        read_only_fields = [
            "upload_id",
            "file_size",
            "status",
            "md5",
            "original_filename",
        ]

    def validate_file(self, value):
        # We only check Extension here.
        # For 10GB, we skip size check and move that to the background worker.
        is_valid, error_msg = validate_file(value, max_size=10 * 1024 * 1024 * 1024)
        if not is_valid:
            raise serializers.ValidationError(error_msg)
        return value

    def create(self, validated_data):
        uploaded_file = validated_data["file"]
        user = self.context["request"].user

        # We SAVE IMMEDIATELY. No MD5 calculation here!
        return File.objects.create(
            user=user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            status="PENDING",  # It's waiting for the background worker
        )
