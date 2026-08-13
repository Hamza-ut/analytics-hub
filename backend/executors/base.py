from abc import ABC, abstractmethod


class BaseExecutor(ABC):

    @abstractmethod
    def submit_timepoint_run(self, run_instance) -> str:
        """Submits a Timepoint Run job and returns a string Job ID."""
        pass

    @abstractmethod
    def get_job_status(self, job_id: str) -> str:
        """Returns job status ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED')."""
        pass
