from django.db import models
from projects.models import Project
from uploads.models import File


class StrainQCConfig(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="strainqc_config")
    reads_files = models.ManyToManyField(File, related_name="strainqc_reads")
    reference_file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, related_name="strainqc_reference")
    polymorphism_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StrainQCConfig({self.project.project_id})"


class StrainQCResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="strainqc_result")
    result_json = models.JSONField(default=dict)
    ran_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StrainQCResult({self.project.project_id})"
