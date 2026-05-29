from django.db import migrations


def seed_pipelines(apps, schema_editor):
    Pipeline = apps.get_model("projects", "Pipeline")
    Pipeline.objects.bulk_create(
        [
            Pipeline(
                pipeline_name="TIMEPOINT",
                display_name="Optimal Timepoint",
                description="Identifies the optimal measurement window for dose-response curve modelling.",
                is_active=True,
            ),
            Pipeline(
                pipeline_name="STRAIN_QC",
                display_name="Strain QC",
                description="Strain quality control pipeline (in development).",
                is_active=True,
            ),
        ]
    )


def unseed_pipelines(apps, schema_editor):
    Pipeline = apps.get_model("projects", "Pipeline")
    Pipeline.objects.filter(pipeline_name__in=["TIMEPOINT", "STRAIN_QC"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_pipelines, unseed_pipelines),
    ]
