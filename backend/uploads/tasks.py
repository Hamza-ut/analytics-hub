from celery import shared_task
from .models import File
from .utils import calculate_md5


@shared_task
def process_file_checksum(file_id):
    file_obj = File.objects.get(id=file_id)

    try:
        # Calculate MD5 using your chunked utility
        # This can now take 10 minutes and won't break the API!
        md5_result = calculate_md5(file_obj.file)

        file_obj.md5 = md5_result
        file_obj.status = "UPLOADED"
        file_obj.save()
    except Exception as e:
        file_obj.status = "ERROR"
        file_obj.save()
