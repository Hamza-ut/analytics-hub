import os
import json
import logging
import requests
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

_slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
_teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")


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


def send_notification(message):
    """Send message to all configured notification channels (Slack + Teams)."""
    results = {}

    if _slack_webhook:
        try:
            resp = requests.post(
                _slack_webhook,
                data=json.dumps({"text": message}),
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            results["slack"] = resp.status_code == 200
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            results["slack"] = False

    if _teams_webhook:
        try:
            teams_payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": "Pipeline Alert",
                "themeColor": "0076D7",
                "title": "Pipeline Status Update",
                "text": message.replace("*", "").replace("`", ""),
            }
            resp = requests.post(_teams_webhook, json=teams_payload, timeout=10)
            results["teams"] = resp.status_code in (200, 201, 202)
        except Exception as e:
            logger.error(f"Teams notification failed: {e}")
            results["teams"] = False

    return results


def external_notify(project, status="starting", error=None):
    """Build and send a status notification for a project run."""
    user_name = getattr(project.user, "username", "unknown")
    workflow_name = str(project.workflow)
    duration = project.duration.total_seconds() if project.duration else 0

    if status == "starting":
        msg = (
            f"🟠 *Starting:* {workflow_name} workflow — "
            f"project `{project.project_id}` initiated by *{user_name}*"
        )
    elif status == "success":
        msg = (
            f"🟢 *Success:* {workflow_name} workflow — "
            f"project `{project.project_id}` completed in {duration:.2f}s"
        )
    elif status == "failed":
        msg = (
            f"🔴 *Failed:* {workflow_name} workflow — "
            f"project `{project.project_id}` failed after {duration:.2f}s\n"
            f"Error: {str(error)[:200]}"
        )
    else:
        msg = f"❓ *Unknown status* for project `{project.project_id}`"

    send_notification(msg)
