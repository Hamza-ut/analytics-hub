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
| `hpc_services/` | SSH/SFTP/SLURM utilities for Rocket HPC — enabled via `USE_HPC=True` |
| `hpc_jobs/` | Scripts deployed to Rocket cluster (`run_analysis.py`, `submit_drc.sh`) |

## Running with Docker

```bash
docker-compose up --build
```

Migrations and static file collection run automatically via `entrypoint.sh` on startup.

## Running Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Celery worker + Beat (separate terminal):

```bash
source .venv/bin/activate
python -m celery -A config worker --beat -l info
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
| `USE_HPC` | `True` to route uploads and pipeline jobs to Rocket HPC; `False` for local mode |
| `HPC_HOST` | HPC cluster hostname (default: `rocket.hpc.ut.ee`) |
| `HPC_USERNAME` | SSH username on Rocket |
| `HPC_PRIVATE_KEY_PATH` | Path to SSH private key (default: `~/.ssh/rocket_personal_private.key`) |
| `HPC_INPUT_DATA_BASE` | Base path for uploaded files on Rocket |
| `HPC_PROJECT_BASE` | Root of the analytics-hub project directory on Rocket |
| `HPC_DRC_TIMEPOINT_SBATCH` | Path to the SLURM batch script on Rocket |

## Key Models

| Model | App | Description |
|---|---|---|
| `User` | Django built-in | Standard user, identified by username + email |
| `File` | uploads | Uploaded file with MD5, status, and storage path |
| `Pipeline` | projects | Registered pipeline — `pipeline_name` (routing key), `display_name`, `is_active` |
| `ProjectRun` | projects | A pipeline execution — FK to Pipeline, links user and files, holds config JSON, status, and `slurm_job_id` |
| `TimepointResult` | projects | One-to-one result store for a ProjectRun (TIMEPOINT pipeline) |
