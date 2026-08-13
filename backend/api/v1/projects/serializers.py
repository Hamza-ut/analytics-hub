from rest_framework import serializers
from projects.models import Workflow, Project


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = (
            "workflow_id",
            "name",
            "display_name",
            "description",
            "created_at",
            "is_active",
        )

    def create(self, validated_data):
        return Workflow.objects.create(**validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    # It is used for read-only fields, which is suitable for displaying data in API responses.
    username = serializers.ReadOnlyField(source="user.username")

    # Option B, use slug field when you are writing, even though we are writing to projects table but we are using the workflow name as reference to the workflow table
    workflow = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Workflow.objects.filter(is_active=True),
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "project_id",
            "workflow",
            "status",
            "created_at",
            "started_at",
            "completed_at",
            "duration",
            "error_message",
            "username",
        ]
        read_only_fields = [
            "project_id",
            "username",
            "status",
            "created_at",
            "started_at",
            "completed_at",
            "duration",
            "error_message",
        ]

    def create(self, validated_data):
        # Automatically attach logged-in user
        user = self.context["request"].user
        return Project.objects.create(user=user, **validated_data)
