import os
import json
import re
import logging
from dotenv import load_dotenv

from executors.hpc.connection import get_hpc_client

load_dotenv()
logger = logging.getLogger(__name__)

HPC_BASE = os.getenv(
    "HPC_PROJECT_BASE", "/gpfs/helios/home/hamza/projects/analytics-hub"
)
HPC_INPUT_BASE = f"{HPC_BASE}/input_data"
HPC_OUTPUT_BASE = f"{HPC_BASE}/output_data"
HPC_DRC_TIMEPOINT_SBATCH = os.getenv(
    "HPC_DRC_TIMEPOINT_SBATCH", f"{HPC_BASE}/jobs/submit_drc.sh"
)


def submit_timepoint_job(project):
    """
    Builds HPC config, uploads it, submits sbatch, returns SLURM job ID.
    """
    tp_run = project.timepoint_run
    file_obj = tp_run.files.first()
    file_name = os.path.basename(file_obj.file.name)
    hpc_file_path = f"{HPC_INPUT_BASE}/{file_obj.upload_id}/{file_name}"

    output_dir = f"{HPC_OUTPUT_BASE}/{project.project_id}"
    config_path = f"{output_dir}/config.json"
    results_path = f"{output_dir}/results.json"

    hpc_config = {
        "file_path": hpc_file_path,
        "group_fields": tp_run.group_fields,
        "dose_field": tp_run.dose_field,
        "od_field": tp_run.od_field,
        "time_field": tp_run.time_field,
        "top_n": 3,
        "output_path": results_path,
    }

    client = get_hpc_client()
    try:
        # Create per-project output directory
        _, stdout, _ = client.exec_command(f"mkdir -p {output_dir}")
        stdout.channel.recv_exit_status()
        logger.debug(f"Created HPC output dir: {output_dir}")

        # Upload config.json
        sftp = client.open_sftp()
        with sftp.file(config_path, "w") as f:
            json.dump(hpc_config, f, indent=2)
        sftp.close()
        logger.info(f"Config uploaded: {config_path}")

        # Submit sbatch — pass --output dynamically so logs go into the project folder
        sbatch_cmd = (
            f"sbatch --output={output_dir}/slurm_%j.log "
            f"{HPC_DRC_TIMEPOINT_SBATCH} {config_path}"
        )
        _, stdout, stderr = client.exec_command(sbatch_cmd)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            raise IOError(f"sbatch failed: {stderr.read().decode().strip()}")

        sbatch_output = stdout.read().decode().strip()
        logger.info(f"sbatch response: {sbatch_output}")

        match = re.search(r"\d+", sbatch_output)
        if not match:
            raise ValueError(
                f"Could not extract job ID from sbatch output: {sbatch_output}"
            )

        job_id = match.group()
        logger.info(f"SLURM job {job_id} submitted for {project.project_id}")
        return job_id

    finally:
        client.close()


def check_job_status(job_id):
    """
    Returns 'RUNNING', 'COMPLETED', or 'FAILED'.
    Uses squeue for active jobs, sacct for finished ones.
    """
    client = get_hpc_client()
    try:
        # Check if job is still in the queue
        _, stdout, _ = client.exec_command(f"squeue -j {job_id} -h -o %T 2>/dev/null")
        stdout.channel.recv_exit_status()
        queue_state = stdout.read().decode().strip()

        if queue_state in ("RUNNING", "PENDING", "CONFIGURING", "COMPLETING"):
            logger.debug(f"Job {job_id} is active: {queue_state}")
            return "RUNNING"

        # Job not in queue — check sacct for final state
        _, stdout, _ = client.exec_command(
            f"sacct -j {job_id} --format=State -n -P 2>/dev/null | head -1"
        )
        stdout.channel.recv_exit_status()
        sacct_state = stdout.read().decode().strip()

        logger.debug(f"sacct state for job {job_id}: '{sacct_state}'")

        if sacct_state == "COMPLETED":
            return "COMPLETED"
        elif sacct_state in (
            "FAILED",
            "CANCELLED",
            "TIMEOUT",
            "OUT_OF_MEMORY",
            "NODE_FAIL",
        ):
            return "FAILED"

        return "RUNNING"

    finally:
        client.close()


def delete_project_output_from_hpc(project_id):
    """
    Deletes the output_data/prj_xxx/ folder from HPC when a project is deleted.
    Only acts on folders with the prj_ prefix inside HPC_OUTPUT_BASE.
    """
    if not project_id or not project_id.startswith("prj_"):
        logger.warning(
            f"Skipping HPC cleanup — unexpected project_id format: {project_id}"
        )
        return False

    target_dir = f"{HPC_OUTPUT_BASE}/{project_id}"
    expected_base = HPC_OUTPUT_BASE.rstrip("/")

    if not target_dir.startswith(expected_base):
        logger.critical(f"SECURITY: {target_dir} is outside {expected_base}. Aborting.")
        return False

    client = get_hpc_client()
    try:
        safe_cmd = f"rm -rf {expected_base}/{project_id}"
        _, stdout, stderr = client.exec_command(safe_cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise IOError(f"rm failed: {stderr.read().decode().strip()}")
        logger.info(f"HPC output folder deleted: {target_dir}")
        return True
    except Exception as e:
        logger.error(f"HPC output deletion failed for {project_id}: {e}")
        raise e
    finally:
        client.close()


def fetch_timepoint_results(project):
    """
    Downloads results.json from HPC output dir and returns it as a Python list.
    """
    results_path = f"{HPC_OUTPUT_BASE}/{project.project_id}/results.json"

    client = get_hpc_client()
    try:
        sftp = client.open_sftp()
        try:
            with sftp.file(results_path, "r") as f:
                content = f.read()
        finally:
            sftp.close()

        results = json.loads(content)
        logger.info(f"Results fetched for {project.project_id}: {len(results)} rows")
        return results

    finally:
        client.close()
