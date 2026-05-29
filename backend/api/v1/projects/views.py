from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from .serializers import PipelineSerializer, ProjectRunSerializer

from django.shortcuts import get_object_or_404
from django.db import transaction

from projects.models import Pipeline, ProjectRun
from projects.utils import is_stuck
from projects.tasks import run_timepoint, run_sequence


# create project
@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_create(request):
    serializer = ProjectRunSerializer(data=request.data)

    if serializer.is_valid():
        # CRITICAL PIECE: You must pass the user here!
        # This tells the Serializer: "When you hit .save(), use this user."
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# run project
@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_run(request, project_id):
    # 1. First, find the project by ID only
    project = get_object_or_404(ProjectRun, project_id=project_id)

    # 2. Check Permissions:
    # Must be the owner OR a superuser. If neither, kick them out.
    if project.user != request.user and not request.user.is_superuser:
        return Response(
            {"detail": "Not authorized to run this project."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # 3. Status Check (Anti-Double-Click)
    if project.status in ["QUEUED", "RUNNING"] and not is_stuck(project):
        return Response(
            {"message": "Project is already running."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 4. The Reset and Launch
    with transaction.atomic():
        # Clear old results if they exist
        if hasattr(project, "timepoint_result"):
            project.timepoint_result.delete()

        # Reset status
        project.status = "QUEUED"
        project.error_message = None
        project.save()

        # Explicit function for the queue (No Act-Smart Lambdas)
        def queue_task():
            pipeline_name = project.pipeline.pipeline_name
            if pipeline_name == "TIMEPOINT":
                run_timepoint.delay(project.id)
            elif pipeline_name == "STRAIN_QC":
                run_sequence.delay(project.id)
            else:
                project.status = "FAILED"
                project.error_message = f"No task handler for pipeline '{pipeline_name}'."
                project.save()

        transaction.on_commit(queue_task)

    return Response({"status": "QUEUED", "message": "Project execution started."})


# get project results
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_result(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id, user=request.user)

    if project.pipeline.pipeline_name == "TIMEPOINT":
        if hasattr(project, "timepoint_result"):
            raw_results = project.timepoint_result.result_json or []

            # --- RESHAPING LOGIC ---
            reshaped_data = []

            for entry in raw_results:
                # We build a new dictionary, starting with the window
                new_entry = {
                    "rank": entry.get("rank"),
                    "ideal_time_window": entry.get("ideal_time_window"),
                    "condition": entry.get("condition"),
                    "composite_score": round(entry.get("composite_score", 0), 4),
                    # You can pull the rest of the mess here...
                    "details": {
                        "cv": entry.get("cv"),
                        "snr": entry.get("snr"),
                        "correlation": entry.get("correlation"),
                    },
                }
                reshaped_data.append(new_entry)
            # -----------------------

            return Response(reshaped_data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Results not ready."}, status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {"error": "Pipeline not supported for results yet."},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "DELETE"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_detail(request, project_id):
    project = get_object_or_404(ProjectRun, project_id=project_id)

    # --- THE GATEKEEPER ---
    # This checks if the user has ANY business being here.
    # If I don't own it AND I'm not an admin, I'm kicked out immediately.
    if project.user != request.user and not request.user.is_superuser:
        return Response(
            {"detail": "You do not have permission to access this project."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # --- ACTION: VIEW ---
    if request.method == "GET":
        # Both the Owner and Admin reach this line!
        serializer = ProjectRunSerializer(project)
        return Response(serializer.data)

    # --- ACTION: DELETE ---
    if request.method == "DELETE":
        # Here is where we get strict.
        # Even if the 'Gatekeeper' let the Owner in, we check again for Admin status.
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only administrators can delete projects."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Safety check for running projects
        if project.status == "RUNNING":
            return Response(
                {"error": "Cannot delete a running project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.delete()
        return Response(
            {"message": "Project deleted."}, status=status.HTTP_204_NO_CONTENT
        )


# get all projects for a user (admin can see all, regular users see only theirs)
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def projects_list(request):
    # If we are here, the user is definitely logged in.
    if request.user.is_superuser:
        projects = ProjectRun.objects.all()
    else:
        projects = ProjectRun.objects.filter(user=request.user)

    serializer = ProjectRunSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def pipelines_list(request):
    pipelines = Pipeline.objects.filter(is_active=True)
    serializer = PipelineSerializer(pipelines, many=True)
    return Response(serializer.data)
