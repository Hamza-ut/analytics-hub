from django.contrib import admin
from .models import Pipeline, ProjectRun


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("pipeline_name", "display_name", "is_active")


@admin.register(ProjectRun)
class ProjectRunAdmin(admin.ModelAdmin):
    list_display = (
        "project_id",
        "pipeline",
        "status",
        "slurm_job_id",
        "user",
        "created_at",
        "started_at",
        "completed_at",
        "error_message",
    )
    search_fields = ("project_id", "status", "user__username")
    list_filter = ("status", "pipeline", "created_at")
