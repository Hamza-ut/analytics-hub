import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def celery_upload_file_md5(file_id):
    from uploads.models import File
    from uploads.utils import calculate_md5

    try:
        file_obj = File.objects.get(id=file_id)
    except File.DoesNotExist:
        logger.error(f"Celery Task aborted: File ID {file_id} not found in database.")
        return

    try:
        with file_obj.file.open("rb"):
            file_obj.md5 = calculate_md5(file_obj.file)
        file_obj.status = "UPLOADED"
        file_obj.save()
        logger.info(f"File ID {file_id} processed successfully.")
    except Exception as e:
        logger.error(f"File processing failed for ID {file_id}: {e}")
        file_obj.status = "FAILED"
        file_obj.save()
