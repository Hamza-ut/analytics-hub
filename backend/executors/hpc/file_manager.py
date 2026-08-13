import os
import logging
from dotenv import load_dotenv

from executors.hpc.connection import get_hpc_client

load_dotenv()
HPC_INPUT_DATA_BASE = os.getenv(
    "HPC_INPUT_DATA_BASE", "/gpfs/helios/home/hamza/projects/analytics-hub/input_data/"
)

logger = logging.getLogger(__name__)


def upload_file_to_hpc(local_file_path, upload_id):
    """
    Connects to the HPC cluster, creates a dedicated directory wrapper for the upload_id,
    and securely streams the target local file onto the remote filesystem.
    """
    file_name = os.path.basename(local_file_path)

    base_media_path = HPC_INPUT_DATA_BASE
    if not base_media_path.endswith("/"):
        base_media_path += "/"

    remote_folder = f"{base_media_path}{upload_id}"
    remote_path = f"{remote_folder}/{file_name}"

    logger.debug(
        f"Preparing upload. Local target: {local_file_path} | Remote target: {remote_path}"
    )

    try:
        client = get_hpc_client()
    except Exception as conn_err:
        logger.error(
            f"File manager aborted: Connection dependency failed. Details: {conn_err}"
        )
        raise conn_err

    try:
        logger.info(f"Creating remote infrastructure directory: {remote_folder}")
        stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_folder}")

        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error_msg = stderr.read().decode().strip()
            raise IOError(
                f"HPC cluster rejected directory allocation command. Exit code {exit_status}: {error_msg}"
            )

        logger.info(f"Opening secure SFTP pipeline channel...")
        sftp = client.open_sftp()

        logger.info(f"Streaming data payload over network channel to: {remote_path}")
        sftp.put(local_file_path, remote_path)
        sftp.close()

        logger.info(
            f"Successfully committed data payload to cluster for ID: {upload_id}"
        )
        return remote_path

    except Exception as e:
        logger.error(
            f"Critical execution failure during file upload pipeline: {str(e)}"
        )
        raise e

    finally:
        client.close()
        logger.debug("HPC Client SSH session safely terminated.")


def delete_file_from_hpc(remote_file_path):
    """
    Deletes a file and its parent upl_xxx folder from HPC.
    Only acts on folders with the upl_ prefix inside HPC_INPUT_DATA_BASE.
    """
    remote_folder = os.path.normpath(os.path.dirname(remote_file_path))
    folder_name = os.path.basename(remote_folder)
    expected_base = os.path.normpath(HPC_INPUT_DATA_BASE)

    if not folder_name.startswith("upl_"):
        logger.warning(
            f"Skipping HPC deletion — folder '{folder_name}' lacks upl_ prefix."
        )
        return False

    if not remote_folder.startswith(expected_base):
        logger.critical(
            f"Skipping HPC deletion — {remote_folder} is outside {expected_base}."
        )
        return False

    client = get_hpc_client()
    try:
        _, stdout, stderr = client.exec_command(f"rm -rf {expected_base}/{folder_name}")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise IOError(f"rm failed: {stderr.read().decode().strip()}")
        logger.info(f"Deleted HPC folder: {expected_base}/{folder_name}")
        return True
    except Exception as e:
        logger.error(f"HPC file deletion failed: {e}")
        raise e
    finally:
        client.close()


def download_file_from_hpc(remote_file_path):
    """
    Connects to the HPC cluster and returns an open file-like object
    reading directly from the remote filesystem over SFTP.
    """
    if not remote_file_path or not remote_file_path.startswith("/gpfs/"):
        logger.error(f"Invalid remote path provided for download: {remote_file_path}")
        raise ValueError("Invalid remote HPC file path layout.")

    try:
        client = get_hpc_client()
        sftp = client.open_sftp()

        logger.info(f"Opening remote read pipeline for target: {remote_file_path}")

        remote_file = sftp.open(remote_file_path, "rb")

        # Attach handles so the connection stays open until Django finishes streaming
        remote_file.hpc_client = client
        remote_file.hpc_sftp = sftp

        return remote_file

    except Exception as e:
        logger.error(f"Failed to initialize remote read pipeline: {e}")
        raise e


if __name__ == "__main__":
    import secrets

    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    TEST_LOCAL_FILE = "/home/hamza/analytics-hub/backend/media/timepoint_vallo.csv"
    MOCK_UPLOAD_ID = f"upl_test_{secrets.token_hex(2).lower()}"

    print(f"\nSTEP 1: Testing Isolated Upload...")
    try:
        resulting_remote_path = upload_file_to_hpc(TEST_LOCAL_FILE, MOCK_UPLOAD_ID)
        print(f"UPLOAD SUCCESS! Remote path: {resulting_remote_path}")

        print(f"\nSTEP 2: Testing Isolated Deletion of that exact folder...")
        deletion_success = delete_file_from_hpc(resulting_remote_path)
        if deletion_success:
            print(f"DELETION SUCCESS! Rocket storage wiped clean.\n")

    except Exception as e:
        print(f"\nTEST FAILED! Exception caught: {e}\n")
