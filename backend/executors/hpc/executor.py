import logging
from executors.base import BaseExecutor

logger = logging.getLogger(__name__)


class HPCExecutor(BaseExecutor):

    def submit_timepoint_run(self, run_instance) -> str:
        raise NotImplementedError("HPC job submission not yet implemented.")

    def get_job_status(self, job_id: str) -> str:
        raise NotImplementedError("HPC job status not yet implemented.")
