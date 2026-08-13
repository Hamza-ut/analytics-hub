import secrets
import logging
from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def generate_project_id():
    return f"prj_{secrets.token_hex(3).lower()}"


class Workflow(models.Model):
    workflow_id = models.CharField(
        max_length=20, unique=True, blank=True, editable=False
    )
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.workflow_id:
            self.workflow_id = f"w{self.pk}"
            Workflow.objects.filter(pk=self.pk).update(workflow_id=self.workflow_id)

    def __repr__(self):
        return f"Workflow(workflow_id='{self.workflow_id}', name='{self.name}', display_name='{self.display_name}')"

    def __str__(self):
        return self.display_name


class Project(models.Model):
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
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.PROTECT,
        related_name="projects",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    executor_job_id = models.CharField(max_length=255, blank=True, null=True)

    def __repr__(self):
        return f"Project(id={self.id}, project_id='{self.project_id}', status='{self.status}')"

    def __str__(self):
        return self.project_id
