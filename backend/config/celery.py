import os
import logging
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Silence paramiko's verbose handshake debug output in Celery workers
logging.getLogger("paramiko").setLevel(logging.WARNING)

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
