from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .serializers import PipelineSerializer, ProjectRunSerializer

from django.shortcuts import get_object_or_404
from django.db import transaction

from projects.models import Pipeline, ProjectRun
from projects.utils import is_stuck
from projects.tasks import run_timepoint, run_sequence


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_create(request):
    serializer = ProjectRunSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_run(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id)

    if project.user != request.user and not request.user.is_superuser:
        return Response({"detail": "Not authorized to run this project."}, status=status.HTTP_403_FORBIDDEN)

    if project.status in ["QUEUED", "RUNNING"] and not is_stuck(project):
        return Response({"message": "Project is already running."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        if hasattr(project, "timepoint_result"):
            project.timepoint_result.delete()

        project.status = "QUEUED"
        project.error_message = None
        project.slurm_job_id = None
        project.started_at = None
        project.completed_at = None
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

    return Response({"status": "QUEUED", "message": "Project execution started."})


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_result(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id, user=request.user)

    if project.pipeline.pipeline_name == "TIMEPOINT":
        if hasattr(project, "timepoint_result"):
            raw_results = project.timepoint_result.result_json or []
            reshaped = [
                {
                    "rank": entry.get("rank"),
                    "ideal_time_window": entry.get("ideal_time_window"),
                    "condition": entry.get("condition"),
                    "composite_score": round(entry.get("composite_score", 0), 4),
                    "details": {
                        "cv": entry.get("cv"),
                        "snr": entry.get("snr"),
                        "correlation": entry.get("correlation"),
                    },
                }
                for entry in raw_results
            ]
            return Response(reshaped, status=status.HTTP_200_OK)
        return Response({"error": "Results not ready."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"error": "Pipeline not supported for results yet."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_detail(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id)

    if project.user != request.user and not request.user.is_superuser:
        return Response({"detail": "You do not have permission to access this project."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(ProjectRunSerializer(project).data)

    if request.method == "DELETE":
        if not request.user.is_superuser:
            return Response({"detail": "Only administrators can delete projects."}, status=status.HTTP_403_FORBIDDEN)
        if project.status == "RUNNING":
            return Response({"error": "Cannot delete a running project."}, status=status.HTTP_400_BAD_REQUEST)
        project.delete()
        return Response({"message": "Project deleted."}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def projects_list(request):
    if request.user.is_superuser:
        projects = ProjectRun.objects.all()
    else:
        projects = ProjectRun.objects.filter(user=request.user)
    return Response(ProjectRunSerializer(projects, many=True).data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def pipelines_list(request):
    pipelines = Pipeline.objects.filter(is_active=True)
    return Response(PipelineSerializer(pipelines, many=True).data)
