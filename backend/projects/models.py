import os
import secrets
import logging
from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def generate_project_id():
    return f"prj_{secrets.token_hex(3).lower()}"


class Pipeline(models.Model):
    pipeline_name = models.CharField(
        max_length=50, unique=True
    )  # internal routing key, never changes
    display_name = models.CharField(max_length=100)  # human-readable label shown in UI
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class ProjectRun(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("QUEUED", "Queued"),
        ("RUNNING", "Running"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
    ]

    id = models.BigAutoField(primary_key=True)
    project_id = models.CharField(
        max_length=20, unique=True, default=generate_project_id, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    files = models.ManyToManyField("uploads.File", related_name="projects")
    pipeline = models.ForeignKey(Pipeline, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)
    config = models.JSONField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    slurm_job_id = models.CharField(max_length=20, blank=True, null=True)

    def delete(self, *args, **kwargs):
        USE_HPC = os.getenv("USE_HPC", "False") == "True"
        if USE_HPC:
            try:
                from hpc_services.job_manager import delete_project_output_from_hpc
                delete_project_output_from_hpc(self.project_id)
            except Exception as e:
                logger.error(f"HPC output cleanup failed for {self.project_id}: {e}")
        super().delete(*args, **kwargs)

    def __repr__(self):
        return f"ProjectRun(id={self.id}, project_id='{self.project_id}', status='{self.status}')"

    def __str__(self):
        return self.project_id


class TimepointResult(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.OneToOneField(
        ProjectRun, on_delete=models.CASCADE, related_name="timepoint_result"
    )
    result_json = models.JSONField()

    def __str__(self):
        return f"Result for {self.project.project_id}"
