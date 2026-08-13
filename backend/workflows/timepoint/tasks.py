import logging
import pandas as pd
from celery import shared_task
from django.utils import timezone

from projects.models import Project
from projects.utils import external_notify
from workflows.timepoint.models import Run, Result
from external_tools.drc_timepoint import run_analysis_from_config

logger = logging.getLogger(__name__)


@shared_task
def timepoint_run_celery(project_id: str):
    # 1. Fetch DB records
    try:
        project = Project.objects.get(project_id=project_id)
        run = Run.objects.get(project=project)
    except (Project.DoesNotExist, Run.DoesNotExist) as e:
        logger.error(f"[TimepointTask] Record missing for project {project_id}: {e}")
        return

    # 2. Mark START: Set started_at timestamp & trigger 'starting' notification
    project.status = "RUNNING"
    project.started_at = timezone.now()
    project.save(update_fields=["status", "started_at"])

    external_notify(project, status="starting")

    try:
        # 3. Build config for external script
        config = {
            "file_path": run.file.file.path,
            "group_fields": run.group_fields,
            "dose_field": run.dose_field,
            "od_field": run.od_field,
            "time_field": run.time_field,
            "top_n": run.top_n,
        }

        logger.info(
            f"[TimepointTask] Running tool for {project_id} on {config['file_path']}"
        )

        # 4. Execute external pipeline
        result_df: pd.DataFrame = run_analysis_from_config(config)

        if result_df is None or result_df.empty:
            raise ValueError("External DRC tool returned an empty DataFrame.")

        # 5. Convert DataFrame to Python native list of dicts
        json_data = result_df.to_dict(orient="records")

        # 6. Save results to Result table
        Result.objects.update_or_create(
            timepoint_run=run, defaults={"result_json": json_data}
        )

        # 7. Mark SUCCESS: Calculate completed_at and duration
        project.status = "SUCCESS"
        project.completed_at = timezone.now()
        project.duration = project.completed_at - project.started_at
        project.save(update_fields=["status", "completed_at", "duration"])

        # 8. Notify Slack/Teams of success
        external_notify(project, status="success")
        logger.info(f"[TimepointTask] Successfully completed {project_id}")

    except Exception as e:
        logger.exception(f"[TimepointTask] Processing failed for {project_id}: {e}")

        # 9. Mark FAILURE: Update error_message, calculate completed_at and duration
        project.status = "FAILED"
        project.error_message = str(e)
        project.completed_at = timezone.now()
        if project.started_at:
            project.duration = project.completed_at - project.started_at

        project.save(
            update_fields=["status", "error_message", "completed_at", "duration"]
        )

        # 10. Notify Slack/Teams of failure
        external_notify(project, status="failed", error=str(e))
