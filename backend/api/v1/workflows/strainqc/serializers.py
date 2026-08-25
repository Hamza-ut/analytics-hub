from rest_framework import serializers
from workflows.strainqc.models import StrainQCConfig, StrainQCResult


class StrainQCConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrainQCConfig
        fields = [
            "id",
            "project_id",
            "reads_files",
            "reference_file",
            "polymorphism_mode",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    project_id = serializers.CharField(source="project.project_id", read_only=True)


class StrainQCResultSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField(source="project.project_id", read_only=True)

    class Meta:
        model = StrainQCResult
        fields = ["id", "project_id", "result_json", "ran_at"]
        read_only_fields = ["id", "project_id", "ran_at"]
