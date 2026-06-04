import os
import logging

logger = logging.getLogger(__name__)


def stream_file(file_obj):
    """
    Returns an open file handle for streaming as a FileResponse.
    HPC mode: opens directly from Rocket via SFTP.
    Local mode: opens from disk.
    """
    USE_HPC = os.getenv("USE_HPC", "False") == "True"

    if USE_HPC:
        from hpc_services.file_manager import download_file_from_hpc
        hpc_base = os.getenv(
            "HPC_INPUT_DATA_BASE",
            "/gpfs/helios/home/hamza/projects/analytics-hub/input_data/",
        )
        remote_path = os.path.join(hpc_base, file_obj.file.name)
        remote_file = download_file_from_hpc(remote_path)

        # Patch close so the SSH session tears down once Django finishes streaming
        _orig_close = remote_file.close
        def _close_with_hpc_cleanup():
            try:
                _orig_close()
            finally:
                try: remote_file.hpc_sftp.close()
                except Exception: pass
                try: remote_file.hpc_client.close()
                except Exception: pass
        remote_file.close = _close_with_hpc_cleanup
        return remote_file

    return open(file_obj.file.path, "rb")


def delete_file(file_obj):
    """
    Deletes a file completely — cleans up HPC storage if needed, then removes from DB.
    Call this from views instead of file_obj.delete() directly.
    """
    USE_HPC = os.getenv("USE_HPC", "False") == "True"

    if USE_HPC and file_obj.file and file_obj.file.name:
        from hpc_services.file_manager import delete_file_from_hpc
        hpc_base = os.getenv(
            "HPC_INPUT_DATA_BASE",
            "/gpfs/helios/home/hamza/projects/analytics-hub/input_data/",
        )
        remote_path = os.path.join(hpc_base, file_obj.file.name)
        try:
            delete_file_from_hpc(remote_path)
        except Exception as e:
            logger.error(f"HPC deletion failed for {file_obj.upload_id}: {e}")

        # Prevents Django's post_delete signal from trying to remove a
        # non-existent local file (it was already deleted after HPC upload)
        file_obj.file = None

    file_obj.delete()
