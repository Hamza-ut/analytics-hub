import secrets
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# to generate unique upload ids
def generate_upload_id():
    return f"UPL_{secrets.token_hex(3).upper()}"


# to generate file path for uploaded files, we can use the upload_id to create a unique folder for each upload
def upload_file_path(instance, filename):
    return f"{instance.upload_id}/{filename}"


class File(models.Model):
    # similar to postgres enums
    STATUS_CHOICES = [
        ("UPLOADING", "Uploading"),
        ("UPLOADED", "Uploaded"),
        ("FAILED", "Failed"),
    ]
    # DJANGO automatically creates an id field as primary key, but we can override it if we want
    id = models.BigAutoField(primary_key=True)

    upload_id = models.CharField(
        max_length=20,
        unique=True,
        default=generate_upload_id,
        editable=False,
        db_collation="C",
    )
    # foreign key automatically adds _id in the database, so we just call it user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=upload_file_path
    )  # no parenthesis in the function calling, we just pass the function reference
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

    # this is for debugging purposes, it will return the upload_id when we print the object
    def __str__(self):
        return self.upload_id
