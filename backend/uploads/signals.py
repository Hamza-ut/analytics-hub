# uploads/signals.py
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import File


@receiver(post_delete, sender=File)
def delete_file_from_storage(sender, instance, **kwargs):

    if not instance.file:
        return

    file_path = instance.file.path
    folder_path = os.path.dirname(file_path)

    # delete the file
    instance.file.delete(save=False)

    # remove folder if empty
    if os.path.exists(folder_path) and not os.listdir(folder_path):
        os.rmdir(folder_path)
