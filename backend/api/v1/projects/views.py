from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import WorkflowSerializer, ProjectSerializer
from projects.models import Workflow, Project


class WorkflowList(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            workflows = Workflow.objects.all()
            serializer = WorkflowSerializer(workflows, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateProject(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Project created successfully.",
                    "project_id": serializer.data["project_id"],
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetail(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, project_id, user):
        project = get_object_or_404(Project, project_id=project_id)
        if project.user != user and not user.is_superuser:
            raise PermissionDenied("You do not have permission to access this project.")
        return project

    def get(self, request, project_id):
        project = self.get_object(project_id, request.user)
        return Response(ProjectSerializer(project).data)

    def delete(self, request, project_id):
        project = self.get_object(project_id, request.user)
        project.delete()
        return Response(
            {"message": f"Project {project_id} deleted successfully."},
            status=status.HTTP_200_OK,
        )


class ProjectsList(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = (
            Project.objects.all()
            if request.user.is_superuser
            else Project.objects.filter(user=request.user)
        )
        serializer = ProjectSerializer(projects.order_by("-created_at"), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
