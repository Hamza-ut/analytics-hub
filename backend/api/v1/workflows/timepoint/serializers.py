from rest_framework import serializers
from projects.models import Project
from uploads.models import File
from workflows.timepoint.models import Run, Result


class TimepointRunConfigureSerializer(serializers.ModelSerializer):
    project_id = serializers.ReadOnlyField(source="project.project_id")
    # project = serializers.SlugRelatedField(
    #     slug_field="project_id", queryset=Project.objects.all()
    # )
    file = serializers.SlugRelatedField(
        slug_field="upload_id", queryset=File.objects.all()
    )

    class Meta:
        model = Run
        fields = [
            "id",
            "project_id",
            "file",
            "group_fields",
            "dose_field",
            "od_field",
            "time_field",
            "top_n",
        ]

        read_only_fields = ["id", "project_id"]

    def validate_file(self, file):
        user = self.context["request"].user

        # 1. File Ownership Check
        if file.user != user and not user.is_superuser:
            raise serializers.ValidationError("File does not exist or access denied.")

        # 2. File Status Check
        if file.status != "UPLOADED":
            raise serializers.ValidationError(
                f"File '{file.upload_id}' is not fully uploaded or verified yet."
            )

        return file


class TimepointResultsSerializer(serializers.ModelSerializer):
    # Traverses: Result -> Run -> Project -> project_id
    project_id = serializers.ReadOnlyField(source="timepoint_run.project.project_id")

    # Traverses: Result -> Run -> File -> upload_id
    upload_id = serializers.ReadOnlyField(source="timepoint_run.file.upload_id")

    # Traverses: Result -> Run -> File -> original_filename
    filename = serializers.ReadOnlyField(source="timepoint_run.file.original_filename")

    class Meta:
        model = Result
        fields = [
            "id",
            "result_json",
            "ran_at",
            "project_id",
            "upload_id",
            "filename",
        ]

        read_only_fields = fields
