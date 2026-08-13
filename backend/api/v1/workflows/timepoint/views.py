from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from projects.models import Project
from workflows.timepoint.models import Run, Result
from workflows.timepoint.tasks import timepoint_run_celery
from .serializers import TimepointRunConfigureSerializer, TimepointResultsSerializer


class RunConfigure(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.JSONParser]

    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        if project.user != request.user and not request.user.is_superuser:
            return Response(
                {"error": "Project does not exist or access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            run = project.timepoint_run
        except Run.DoesNotExist:
            return Response(
                {"message": "This project has not been configured yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TimepointRunConfigureSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        if project.user != request.user:
            return Response(
                {"error": "Only the project owner can attach a configuration."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.workflow.name != "drctimepoint":
            return Response(
                {"error": f"Project '{project_id}' is not a timepoint workflow."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(project, "timepoint_run"):
            return Response(
                {"error": f"Project '{project_id}' is already configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TimepointRunConfigureSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            run = serializer.save(project=project)
            return Response(
                {
                    "message": "Timepoint configuration attached successfully.",
                    "project_id": run.project.project_id,
                    "run_id": run.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RunExecute(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)
        get_object_or_404(Run, project=project)  # confirms Run is configured

        if project.user != request.user and not request.user.is_superuser:
            return Response(
                {"error": "Project does not exist or access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.status in ("QUEUED", "RUNNING"):
            return Response(
                {"error": f"Project is already {project.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = timepoint_run_celery.delay(project_id)
        project.status = "QUEUED"
        project.executor_job_id = task.id
        project.save(update_fields=["status", "executor_job_id"])

        return Response(
            {
                "message": "Timepoint execution queued successfully.",
                "project_id": project.project_id,
                "status": project.status,
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class RunResults(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)
        run = get_object_or_404(Run, project=project)

        if project.user != request.user and not request.user.is_superuser:
            return Response(
                {"error": "Project does not exist or access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            result = run.timepoint_result
        except Result.DoesNotExist:
            return Response(
                {"message": "No results yet. Run the analysis first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TimepointResultsSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
