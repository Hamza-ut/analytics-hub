import secrets
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def generate_upload_id():
    return f"upl_{secrets.token_hex(3).lower()}"


def upload_file_path(instance, filename):
    return f"{instance.upload_id}/{filename}"


class File(models.Model):
    STATUS_CHOICES = [
        ("UPLOADING", "Uploading/Processing"),
        ("UPLOADED", "Uploaded & Verified"),
        ("FAILED", "Failed"),
    ]

    id = models.BigAutoField(primary_key=True)
    upload_id = models.CharField(
        max_length=20,
        unique=True,
        default=generate_upload_id,
        editable=False,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_file_path)
    original_filename = models.TextField()
    file_size = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    md5 = models.CharField(max_length=64, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.projects.exists():
            raise ValidationError(
                "Cannot delete file: it is used by one or more projects."
            )
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.upload_id
