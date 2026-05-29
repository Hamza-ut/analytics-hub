import os
import json
import requests

from datetime import timedelta
from dotenv import load_dotenv
from django.utils import timezone
from django.shortcuts import get_object_or_404

from uploads.models import File

load_dotenv()

_slack_webhook = os.getenv("SLACK_WEBHOOK_URL")


# ---------------------------------------------------------------------------
# File access helpers
# ---------------------------------------------------------------------------

def get_user_files(user):
    """Return all uploaded files visible to this user (superusers see all)."""
    if user.is_superuser:
        return File.objects.filter(status="UPLOADED")
    return File.objects.filter(user=user, status="UPLOADED")


def get_user_file(user, file_id):
    """Return a single uploaded file, enforcing ownership for non-superusers."""
    if user.is_superuser:
        return get_object_or_404(File, id=file_id, status="UPLOADED")
    return get_object_or_404(File, id=file_id, user=user, status="UPLOADED")


# ---------------------------------------------------------------------------
# Pipeline input validators
# Returns (cleaned_data, error_string) — error is None on success
# ---------------------------------------------------------------------------

# def handle_timepoint(request):
#     """Validate and extract Timepoint pipeline POST data."""
#     file_id = request.POST.get("timepoint_file")
#     group_fields = request.POST.get("group_fields")
#     dose_field = request.POST.get("dose_field")
#     od_field = request.POST.get("od_field")
#     time_field = request.POST.get("time_field")

#     try:
#         file = get_user_file(request.user, file_id)
#     except Exception:
#         return None, "Selected file is invalid or inaccessible."

#     if not file.original_filename.lower().endswith(".csv"):
#         return None, "Only CSV files are allowed for the Timepoint pipeline."

#     if not all([group_fields, dose_field, od_field, time_field]):
#         return None, "Please fill in all required fields."

#     cleaned_data = {
#         "file": file,
#         "group_fields": [f.strip() for f in group_fields.split(",")],
#         "dose_field": dose_field,
#         "od_field": od_field,
#         "time_field": time_field,
#     }
#     return cleaned_data, None


def validate_timepoint_logic(file_obj, config):
    """
    Pure logic: Checks if the file is a CSV and if config is complete.
    """
    if not file_obj.original_filename.lower().endswith(".csv"):
        return False, "Only CSV files are allowed for the Timepoint pipeline."

    required = ["group_fields", "dose_field", "od_field", "time_field"]
    if not all(k in config for k in required):
        return False, "Please fill in all required fields."

    return True, None

def handle_sequence(request):
    """Validate and extract Sequence pipeline POST data."""
    ref_file_id = request.POST.get("ref_file")
    read_file_ids = request.POST.getlist("read_files")

    if not ref_file_id or not read_file_ids:
        return None, "Please select a reference file and at least one read file."

    try:
        ref_file = get_user_file(request.user, ref_file_id)
    except Exception:
        return None, "Selected reference file is invalid or inaccessible."

    read_files = []
    for fid in read_file_ids:
        try:
            read_files.append(get_user_file(request.user, fid))
        except Exception:
            return None, f"One of the read files (ID {fid}) is invalid or inaccessible."

    if len(read_files) > 2:
        return None, "You can select at most 2 read files."

    # Extension validation can be added here when the pipeline is implemented:
    #   ref_file.original_filename.lower().endswith(".fasta")
    #   read_file.original_filename.lower().endswith((".fastq", ".fastq.gz"))

    return {"ref_file": ref_file, "read_files": read_files}, None


# ---------------------------------------------------------------------------
# Stuck-project detection
# ---------------------------------------------------------------------------

def is_stuck(project):
    """
    Returns True if a project has been in a non-terminal state for too long:
      - QUEUED for more than 5 minutes (worker probably never picked it up)
      - RUNNING for more than 4 hours (worker likely crashed mid-run)
    """
    if project.status == "QUEUED":
        return (timezone.now() - project.created_at) > timedelta(minutes=5)

    if project.status == "RUNNING" and project.started_at:
        return (timezone.now() - project.started_at) > timedelta(hours=4)

    return False


# ---------------------------------------------------------------------------
# Slack notifications
# ---------------------------------------------------------------------------

def send_slack_notification(message):
    """Send a plain-text message to the configured Slack webhook. Returns True on success."""
    if not _slack_webhook:
        print("SLACK_WEBHOOK_URL is not set — skipping notification.")
        return False
    try:
        response = requests.post(
            _slack_webhook,
            data=json.dumps({"text": message}),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Slack notification failed: {e}")
        return False


def notify_slack(project, status="starting", error=None):
    """Build and send a status notification for a project run."""
    user_name = getattr(project.user, "username", "unknown")
    duration = project.duration.total_seconds() if project.duration else 0

    if status == "starting":
        msg = (
            f"🟠 *Starting:* {project.pipeline} workflow — "
            f"project `{project.project_id}` initiated by *{user_name}*"
        )
    elif status == "success":
        msg = (
            f"🟢 *Success:* {project.pipeline} workflow — "
            f"project `{project.project_id}` completed in {duration:.2f}s"
        )
    elif status == "failed":
        msg = (
            f"🔴 *Failed:* {project.pipeline} workflow — "
            f"project `{project.project_id}` failed after {duration:.2f}s\n"
            f"Error: {str(error)[:200]}"
        )
    else:
        msg = f"❓ *Unknown status* for project `{project.project_id}`"

    send_slack_notification(msg)
