from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from projects.models import Project
from workflows.strainqc.models import StrainQCConfig, StrainQCResult
from workflows.strainqc.tasks import run_strainqc_task
from .serializers import StrainQCConfigSerializer, StrainQCResultSerializer


class RunConfigure(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        # TODO: create/update StrainQCConfig for this project
        return Response({"message": "not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def get(self, request, project_id):
        # TODO: return existing config for this project
        return Response({"message": "not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)


class RunExecute(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        # TODO: queue run_strainqc_task for this project
        return Response({"message": "not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)


class RunResults(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        # TODO: return StrainQCResult for this project
        return Response({"message": "not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)
