from django.db import models


class Run(models.Model):
    project = models.OneToOneField(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="timepoint_run",
    )
    file = models.ForeignKey(
        "uploads.File",
        on_delete=models.PROTECT,
        related_name="timepoint_runs",
    )
    group_fields = models.JSONField()
    dose_field = models.CharField(max_length=100)
    od_field = models.CharField(max_length=100)
    time_field = models.CharField(max_length=100)
    top_n = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return f"Run({self.project.project_id})"


class Result(models.Model):
    timepoint_run = models.OneToOneField(
        Run,
        on_delete=models.CASCADE,
        related_name="timepoint_result",
    )
    result_json = models.JSONField()
    ran_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result({self.timepoint_run.project.project_id})"
