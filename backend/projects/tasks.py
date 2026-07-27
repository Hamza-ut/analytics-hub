import os
import logging

from celery import shared_task
from django.db import connection
from django.utils import timezone

from .models import ProjectRun
from .utils import external_notify
from projects.models import TimepointResult
from drc_timepoint import run_analysis_from_config

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_timepoint(self, project_id):
    project = ProjectRun.objects.get(id=project_id)

    external_notify(project, status="starting")

    project.status = "RUNNING"
    project.started_at = timezone.now()
    project.save(update_fields=["status", "started_at"])

    USE_HPC = os.getenv("USE_HPC", "False") == "True"

    # --- HPC MODE ---
    if USE_HPC:
        try:
            from hpc_services.job_manager import submit_timepoint_job

            job_id = submit_timepoint_job(project)
            project.slurm_job_id = job_id
            project.save(update_fields=["slurm_job_id"])
            logger.info(
                f"SLURM job {job_id} submitted for {project.project_id}. Polling will handle completion."
            )
        except Exception as e:
            logger.error(f"HPC submission failed for {project.project_id}: {e}")
            project.status = "FAILED"
            project.error_message = str(e)
            project.completed_at = timezone.now()
            project.duration = project.completed_at - project.started_at
            project.save()
            external_notify(project, status="failed", error=e)
        finally:
            connection.close()
        return

    # --- LOCAL MODE ---
    try:
        file_obj = project.files.first()
        file_path = file_obj.file.path

        config = {
            "file_path": file_path,
            "group_fields": project.config.get("group_fields", []),
            "dose_field": project.config.get("dose_field"),
            "od_field": project.config.get("od_field"),
            "time_field": project.config.get("time_field"),
        }

        result_df = run_analysis_from_config(config)

        TimepointResult.objects.update_or_create(
            project=project,
            defaults={"result_json": result_df.to_dict(orient="records")},
        )

        project.status = "SUCCESS"
        project.completed_at = timezone.now()
        project.duration = project.completed_at - project.started_at
        external_notify(project, status="success")

    except Exception as e:
        project.status = "FAILED"
        project.error_message = str(e)
        project.completed_at = timezone.now()
        project.duration = project.completed_at - project.started_at
        external_notify(project, status="failed", error=e)

    finally:
        if not project.completed_at:
            project.completed_at = timezone.now()
        if project.started_at and not project.duration:
            project.duration = project.completed_at - project.started_at
        project.save()
        connection.close()


@shared_task
def poll_hpc_jobs():
    """
    Celery Beat periodic task — runs every 30 seconds.
    Checks SLURM status for all RUNNING projects with a slurm_job_id.
    On completion downloads results and saves to DB.
    """
    from hpc_services.job_manager import check_job_status, fetch_timepoint_results

    hpc_jobs = ProjectRun.objects.filter(
        status="RUNNING",
        slurm_job_id__isnull=False,
    ).exclude(slurm_job_id="")

    if not hpc_jobs.exists():
        return

    logger.info(f"Polling {hpc_jobs.count()} active HPC job(s)...")

    for project in hpc_jobs:
        try:
            status = check_job_status(project.slurm_job_id)
            logger.info(f"Job {project.slurm_job_id} ({project.project_id}): {status}")

            if status == "COMPLETED":
                if project.pipeline.pipeline_name == "TIMEPOINT":
                    results = fetch_timepoint_results(project)
                    TimepointResult.objects.update_or_create(
                        project=project,
                        defaults={"result_json": results},
                    )

                project.status = "SUCCESS"
                project.completed_at = timezone.now()
                if project.started_at:
                    project.duration = project.completed_at - project.started_at
                project.save()
                external_notify(project, status="success")
                logger.info(f"Project {project.project_id} completed.")

            elif status == "FAILED":
                project.status = "FAILED"
                project.error_message = (
                    f"SLURM job {project.slurm_job_id} failed on HPC. "
                    f"Check: output_data/{project.project_id}/slurm_{project.slurm_job_id}.log"
                )
                project.completed_at = timezone.now()
                if project.started_at:
                    project.duration = project.completed_at - project.started_at
                project.save()
                external_notify(project, status="failed", error=None)
                logger.error(
                    f"Project {project.project_id} failed (job {project.slurm_job_id})."
                )

        except Exception as e:
            logger.error(
                f"Error polling SLURM job {project.slurm_job_id} "
                f"for {project.project_id}: {e}"
            )

    connection.close()


@shared_task(bind=True)
def run_sequence(self, project_id):
    """
    Placeholder — sequence analysis not yet implemented.
    """
    # add external notification for starting and failing (since it will fail immediately)
    project = ProjectRun.objects.get(id=project_id)

    external_notify(project, status="starting")

    project.status = "FAILED"
    project.error_message = "Sequence pipeline is not yet implemented."
    project.completed_at = timezone.now()
    project.save()

    external_notify(project, status="failed", error=project.error_message)

    connection.close()
