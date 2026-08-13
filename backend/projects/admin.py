from django.contrib import admin
from .models import Project, Workflow


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("workflow_id", "name", "display_name", "is_active")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_id",
        "workflow",
        "status",
        "user",
        "created_at",
        "started_at",
        "completed_at",
        "duration",
    )
    list_filter = ("status", "workflow", "user")
    search_fields = ("project_id", "workflow__display_name", "user__username")
