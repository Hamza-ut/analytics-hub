from rest_framework import serializers
from projects.models import Pipeline, ProjectRun


def validate_timepoint_config(config):
    if not config:
        raise serializers.ValidationError(
            {"config": "Config is required for TIMEPOINT."}
        )
    required = ["group_fields", "dose_field", "od_field", "time_field"]
    if not all(k in config for k in required):
        raise serializers.ValidationError(
            {"config": "Please fill in all required fields: group_fields, dose_field, od_field, time_field."}
        )


class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = ["id", "pipeline_name", "display_name", "description"]


class ProjectRunSerializer(serializers.ModelSerializer):
    pipeline = serializers.SlugRelatedField(
        queryset=Pipeline.objects.filter(is_active=True),
        slug_field="pipeline_name",
    )

    class Meta:
        model = ProjectRun
        fields = ["project_id", "pipeline", "status", "config", "files", "created_at"]
        read_only_fields = ["project_id", "status", "created_at", "user"]

    def to_internal_value(self, data):
        if "pipeline" in data and isinstance(data["pipeline"], str):
            data["pipeline"] = data["pipeline"].upper()
        return super().to_internal_value(data)

    def validate(self, data):
        pipeline = data.get("pipeline")  # Pipeline object resolved by SlugRelatedField
        files = data.get("files", [])
        config = data.get("config", {})

        if not files:
            raise serializers.ValidationError(
                {"files": "You must attach at least one file."}
            )

        if pipeline.pipeline_name == "TIMEPOINT":
            for file_obj in files:
                if not file_obj.original_filename.lower().endswith(".csv"):
                    raise serializers.ValidationError(
                        {"files": f"File '{file_obj.original_filename}' must be a CSV for Timepoint."}
                    )
            validate_timepoint_config(config)

        return data
