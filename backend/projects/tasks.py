import time

from celery import shared_task
from django.db import connection
from django.utils import timezone

from .models import ProjectRun
from .utils import notify_slack
from projects.models import TimepointResult
from drc_timepoint import run_analysis_from_config


@shared_task(bind=True)
def run_timepoint(self, project_id):
    project = ProjectRun.objects.get(id=project_id)

    notify_slack(project, status="starting")

    project.status = "RUNNING"
    project.started_at = timezone.now()
    project.save(update_fields=["status", "started_at"])

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

        # Simulate long-running task — remove in production
        # time.sleep(5)

        result_df = run_analysis_from_config(config)

        TimepointResult.objects.update_or_create(
            project=project,
            defaults={"result_json": result_df.to_dict(orient="records")},
        )

        project.status = "SUCCESS"
        project.completed_at = timezone.now()
        project.duration = project.completed_at - project.started_at
        notify_slack(project, status="success")  # ✅ duration is set

    except Exception as e:
        project.status = "FAILED"
        project.error_message = str(e)
        project.completed_at = timezone.now()
        project.duration = project.completed_at - project.started_at
        notify_slack(project, status="failed", error=e)  # ✅ duration is set here too

    finally:
        if not project.completed_at:  # safety net
            project.completed_at = timezone.now()
        if project.started_at and not project.duration:
            project.duration = project.completed_at - project.started_at
        project.save()
        connection.close()


@shared_task(bind=True)
def run_sequence(self, project_id):
    """
    Placeholder — sequence analysis not yet implemented.
    Follow the same pattern as run_timepoint when ready:
      1. Set status RUNNING, notify Slack
      2. Get file paths from project.files
      3. Run analysis, save results to SequenceResult
      4. Set status SUCCESS/FAILED, notify Slack
      5. Save timestamps, close connection in finally block
    """
    project = ProjectRun.objects.get(id=project_id)
    project.status = "FAILED"
    project.error_message = "Sequence pipeline is not yet implemented."
    project.completed_at = timezone.now()
    project.save()
    connection.close()
