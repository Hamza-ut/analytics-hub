# Backend

Django + Django REST Framework backend for the analytics-hub platform.

## Apps

| App | Purpose |
|---|---|
| `config/` | Project-level settings, root URL conf, Celery app, WSGI/ASGI |
| `accounts/` | User registration, login, logout — Django auth + DRF token auth |
| `uploads/` | File upload and management — CSV/FASTQ/FASTA, async MD5 checksum via Celery |
| `projects/` | Pipeline runs — `ProjectRun` model, Celery tasks, result storage |
| `dashboard/` | User dashboard view (Django template, to be replaced by React) |
| `api/v1/` | DRF router — aggregates serializers and views for accounts, uploads, projects |
| `drc_timepoint/` | First analysis pipeline: dose-response curve timepoint optimizer |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `ENV` | `dev` / `prod` / `ci` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL credentials |
| `CELERY_BROKER_URL` | Redis URL for Celery broker (default: `redis://localhost:6379/3`) |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery results (default: `redis://localhost:6379/4`) |
| `SLACK_WEBHOOK_URL` | Slack webhook for pipeline notifications |
| `HPC_USERNAME` | Username on the Rocket HPC cluster |

## Running Celery

```bash
source .venv/bin/activate
python -m celery -A config worker -l info
```

## Key Models

| Model | App | Description |
|---|---|---|
| `User` | Django built-in | Standard user, identified by username + email |
| `File` | uploads | Uploaded file with MD5, status, and storage path |
| `Pipeline` | projects | Registered pipeline — `pipeline_name` (routing key), `display_name`, `is_active` |
| `ProjectRun` | projects | A pipeline execution — FK to Pipeline, links user and files, holds config JSON and status |
| `TimepointResult` | projects | One-to-one result store for a ProjectRun (TIMEPOINT pipeline) |
