import uuid
import logging
from ..base import BaseExecutor
from workflows.timepoint.tasks import process_timepoint_run_task

logger = logging.getLogger(__name__)


class LocalServerExecutor(BaseExecutor):

    def submit_timepoint_run(self, run_instance) -> str:
        # Get the project_id string (e.g. "prj_1d168f")
        project_id = run_instance.project.project_id

        # Dispatch task to background Celery worker
        task = process_timepoint_run_task.delay(project_id)

        logger.info(
            f"[CeleryExecutor] Dispatched Task ID '{task.id}' for Project '{project_id}'"
        )

        # Return the actual Celery Task ID!
        return str(task.id)

    def get_job_status(self, job_id: str) -> str:
        from celery.result import AsyncResult

        res = AsyncResult(job_id)
        return res.status
