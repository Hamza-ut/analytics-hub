from django.core.management.base import BaseCommand
from projects.models import Workflow

WORKFLOWS = [
    {
        "name": "drctimepoint",
        "display_name": "DRC Optimal Timepoint",
        "description": "Identifies the optimal measurement timepoint for dose-response curve experiments.",
        "is_active": True,
    },
    {
        "name": "strainqc",
        "display_name": "Strain QC",
        "description": "Strain quality control pipeline.",
        "is_active": True,
    },
]


class Command(BaseCommand):
    help = "Seeds the Workflow table if it is empty."

    def handle(self, *args, **options):
        if Workflow.objects.exists():
            self.stdout.write("Workflows already seeded, skipping.")
            return

        for data in WORKFLOWS:
            Workflow.objects.create(**data)

        self.stdout.write(f"Seeded {len(WORKFLOWS)} workflows.")
