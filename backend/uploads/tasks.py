import os
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def process_file_pipeline_task(file_id):
    from uploads.models import File
    from uploads.utils import calculate_md5

    try:
        file_obj = File.objects.get(id=file_id)
    except File.DoesNotExist:
        logger.error(f"Celery Task aborted: File ID {file_id} not found in database.")
        return

    USE_HPC = os.getenv("USE_HPC", "False") == "True"

    try:
        local_file_path = file_obj.file.path

        if USE_HPC:
            from hpc_services.file_manager import upload_file_to_hpc
            from hpc_services.connection import get_hpc_client

            # 1. Upload file to Rocket
            upload_file_to_hpc(local_file_path, file_obj.upload_id)

            # 2. Calculate MD5 on Rocket (file already lives there)
            hpc_base = os.getenv(
                "HPC_INPUT_DATA_BASE",
                "/gpfs/helios/home/hamza/projects/analytics-hub/input_data/",
            )
            absolute_remote_path = os.path.join(hpc_base, file_obj.file.name)

            client = get_hpc_client()
            try:
                _, stdout, stderr = client.exec_command(f"md5sum {absolute_remote_path}")
                exit_status = stdout.channel.recv_exit_status()
                if exit_status == 0:
                    file_obj.md5 = stdout.read().decode().strip().split()[0]
                    file_obj.status = "UPLOADED"
                else:
                    raise IOError(f"md5sum failed on Rocket: {stderr.read().decode()}")
            finally:
                client.close()

            # 3. Delete local copy — file now lives on Rocket only
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            local_dir = os.path.dirname(local_file_path)
            if os.path.exists(local_dir) and not os.listdir(local_dir):
                os.rmdir(local_dir)

        else:
            # Local mode — calculate MD5 here
            file_obj.md5 = calculate_md5(file_obj.file)
            file_obj.status = "UPLOADED"

        file_obj.save()
        logger.info(f"File ID {file_id} processed successfully.")

    except Exception as e:
        logger.error(f"File processing failed for ID {file_id}: {e}")
        file_obj.status = "FAILED"
        file_obj.save()
