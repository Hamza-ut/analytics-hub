from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Pipeline, ProjectRun
from .tasks import run_timepoint, run_sequence  # used by run_project_celery
from .utils import handle_sequence, is_stuck, get_user_files, validate_timepoint_logic, get_user_file


@login_required
def create_project(request):
    user_files = get_user_files(request.user)
    pipelines = Pipeline.objects.filter(is_active=True)

    if request.method == "POST":
        pipeline_name = request.POST.get("pipeline", "").upper()
        pipeline_obj = get_object_or_404(Pipeline, pipeline_name=pipeline_name, is_active=True)

        if pipeline_name == "TIMEPOINT":
            file_id = request.POST.get("timepoint_file")
            file_obj = get_user_file(request.user, file_id)

            config_data = {
                "group_fields": [f.strip() for f in request.POST.get("group_fields", "").split(",")],
                "dose_field": request.POST.get("dose_field"),
                "od_field": request.POST.get("od_field"),
                "time_field": request.POST.get("time_field"),
            }

            is_valid, error = validate_timepoint_logic(file_obj, config_data)
            if not is_valid:
                return render(request, "projects/project.html", {
                    "user_files": user_files, "pipelines": pipelines, "error": error
                })

            project = ProjectRun.objects.create(
                user=request.user,
                pipeline=pipeline_obj,
                config=config_data,
            )
            project.files.add(file_obj)
            return redirect("dashboard:dashboard")

        elif pipeline_name == "STRAIN_QC":
            cleaned_data, error = handle_sequence(request)
            if error:
                return render(request, "projects/project.html", {
                    "user_files": user_files, "pipelines": pipelines, "error": error
                })

            project = ProjectRun.objects.create(user=request.user, pipeline=pipeline_obj)
            project.files.add(cleaned_data["ref_file"], *cleaned_data["read_files"])
            return redirect("dashboard:dashboard")

    return render(request, "projects/project.html", {
        "user_files": user_files, "pipelines": pipelines, "error": None
    })


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id)

    result = None
    if project.pipeline.pipeline_name == "TIMEPOINT":
        if hasattr(project, "timepoint_result"):
            result = project.timepoint_result

    return render(request, "projects/project_detail.html", {
        "project": project,
        "result": result,
    })


@login_required
def run_project_celery(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id)

    if project.status in ["QUEUED", "RUNNING"] and not is_stuck(project):
        return redirect("dashboard:dashboard")

    with transaction.atomic():
        if hasattr(project, "timepoint_result"):
            project.timepoint_result.delete()

        project.status = "QUEUED"
        project.error_message = None
        project.started_at = None
        project.completed_at = None
        project.slurm_job_id = None
        project.save()

        def queue_task():
            try:
                pipeline_name = project.pipeline.pipeline_name
                if pipeline_name == "TIMEPOINT":
                    run_timepoint.delay(project.id)
                elif pipeline_name == "STRAIN_QC":
                    run_sequence.delay(project.id)
                else:
                    project.status = "FAILED"
                    project.error_message = f"No task handler for pipeline '{pipeline_name}'."
                    project.save()
            except Exception:
                project.status = "FAILED"
                project.error_message = "Could not connect to Redis. Task not queued."
                project.save()

        transaction.on_commit(queue_task)

    return redirect("dashboard:dashboard")
