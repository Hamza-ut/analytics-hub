from rest_framework import serializers

from uploads.models import File
from uploads.utils import allowed_extension_and_size_check


class FileSerializer(serializers.ModelSerializer):
    # convert foreign key userid to username for displaying at frontend
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = File
        fields = [
            "upload_id",
            "file",
            "original_filename",
            "file_size",
            "status",
            "md5",
            "uploaded_at",
            "user",
        ]
        read_only_fields = [
            "upload_id",
            "file_size",
            "status",
            "md5",
            "original_filename",
            "uploaded_at",
            "user",
        ]

    def validate_file(self, value):
        # We check file size and allowed extensions.
        is_valid, error_msg = allowed_extension_and_size_check(value)
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
            status="UPLOADING",  # It's waiting for the background worker
        )
