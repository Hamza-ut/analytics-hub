import os
import logging  # <-- Built-in python logger
import paramiko
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

# Define the logger for this specific file
logger = logging.getLogger(__name__)


def get_hpc_client():
    """
    Initializes and returns an authenticated Paramiko SSHClient connected to Rocket.
    """
    hpc_host = os.getenv("HPC_HOST", "rocket.hpc.ut.ee")  # Default to Rocket if not set
    hpc_username = os.getenv("HPC_USERNAME")
    env_key_path = os.getenv(
        "HPC_PRIVATE_KEY_PATH", "~/.ssh/rocket_personal_private.key"
    )
    private_key_path = os.path.expanduser(env_key_path)

    # Instead of print(), we use logger.debug for background configurations
    logger.debug(
        f"Attempting HPC connection with Username: {hpc_username} | Key: {private_key_path}"
    )

    if not hpc_username or not os.path.exists(private_key_path):
        logger.critical(
            "HPC credentials or private key file are missing from the server environment!"
        )
        raise ValueError(
            "CRITICAL: HPC_USERNAME or a valid HPC_PRIVATE_KEY_PATH file is missing!"
        )

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hpc_host, username=hpc_username, key_filename=private_key_path, timeout=30)
        # Standard confirmation uses .info()
        logger.info("Successfully established SSH handshake with Rocket cluster.")
        return client
    except Exception as e:
        # If it blows up, .error() automatically captures what happened
        logger.error(f"Failed to establish SSH handshake with Rocket cluster: {str(e)}")
        raise e


if __name__ == "__main__":
    # 1. Setup our script's logging format
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 2. THE CHOKE: Force Paramiko to only log warnings or errors, hiding its handshake spam
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    # 3. Fire the connection test
    get_hpc_client()
