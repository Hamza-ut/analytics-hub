# analytics-hub

Biofoundry analysis platform for the Bioengineering Department at the University of Tartu.

## About

analytics-hub is the internal web platform for EU-funded biofoundry project. It provides a pipeline interface for running bioinformatics analyses, managing research data files, and submitting compute jobs to the university HPC cluster.

The platform is designed to host multiple analysis pipelines. The first pipeline currently implemented is **drc_timepoint**, a small tool for identifying optimal timepoint for DRC modelling.
It's not a compute heavy tool so some sleep time added for it to mimic the slow compute heavy pipeline.
Actual compute heavy workflows by Marko will come here later

## Current State

The REST API is complete and functional. The frontend is currently in active development — for now the platform uses Django HTML templates for the UI. The React frontend (`frontend/`) is being built in parallel and will replace the templates once ready.

The platform runs in Docker for development. Gunicorn serves the Django application and Nginx runs on the host OS as a reverse proxy.

HPC integration (Rocket cluster via SSH/SFTP + SLURM) is implemented and can be enabled by setting `USE_HPC=True` in `.env`. It is not in active use for the current deployment.

## Tech Stack

| Layer                     | Technology                             |
| ------------------------- | -------------------------------------- |
| Backend                   | Django 4.2, Django REST Framework 3.17 |
| Application server        | Gunicorn                               |
| Reverse proxy             | Nginx (host OS)                        |
| Database                  | PostgreSQL                             |
| Task queue                | Celery 5.6 + Redis                     |
| Analysis engine           | pandas, numpy, scikit-learn            |
| HPC (optional)            | Paramiko 5.0, Rocket cluster (SLURM)   |
| Containerisation          | Docker, docker-compose                 |
| Frontend (current)        | Django HTML templates                  |
| Frontend (in development) | React 19, Vite, Axios                  |

## Prerequisites

**With Docker (recommended for dev):**
- Docker and docker-compose

**Without Docker:**
- Python 3.12+, Node.js 18+, PostgreSQL, Redis

## Getting Started

### Option A — Docker (recommended)

```bash
docker-compose up --build
```

The backend will be available at `http://localhost:8000`.

To run with Nginx on the host:

```bash
sudo cp backend/nginx.conf /etc/nginx/sites-available/analytics-hub
sudo ln -s /etc/nginx/sites-available/analytics-hub /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Option B — Local (manual)

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in DB credentials and secret key
python manage.py migrate
python manage.py runserver
```

```bash
# Celery worker (separate terminal)
cd backend
source .venv/bin/activate
python -m celery -A config worker --beat -l info
```

```bash
# Frontend dev server (separate terminal)
cd frontend
npm install
npm run dev
```

## API Endpoints

**Accounts**

| Method | Endpoint                   | Description           |
| ------ | -------------------------- | --------------------- |
| POST   | `/api/v1/accounts/signup/` | Register a new user   |
| POST   | `/api/v1/accounts/login/`  | Obtain auth token     |
| POST   | `/api/v1/accounts/logout/` | Invalidate auth token |

**Uploads**

| Method      | Endpoint                            | Description                                |
| ----------- | ----------------------------------- | ------------------------------------------ |
| POST        | `/api/v1/uploads/file/`             | Upload a file (CSV/FASTQ/FASTA, max 10 GB) |
| GET, DELETE | `/api/v1/uploads/file/<upload_id>/` | Get or delete a file                       |
| GET         | `/api/v1/uploads/all/`              | List files for the authenticated user      |
| GET         | `/api/v1/uploads/stats/`            | Upload stats for the authenticated user    |

**Projects**

| Method      | Endpoint                                 | Description                              |
| ----------- | ---------------------------------------- | ---------------------------------------- |
| GET         | `/api/v1/projects/pipelines/`            | List available pipelines                 |
| POST        | `/api/v1/projects/create/`               | Create a project with pipeline config    |
| POST        | `/api/v1/projects/run/<project_id>/`     | Queue pipeline execution                 |
| GET         | `/api/v1/projects/results/<project_id>/` | Retrieve analysis results                |
| GET, DELETE | `/api/v1/projects/project/<project_id>/` | Get or delete a project                  |
| GET         | `/api/v1/projects/all/`                  | List projects for the authenticated user |

## Project Structure

```
analytics-hub/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh         collectstatic + migrate + start Gunicorn
│   ├── gunicorn.conf.py      Gunicorn worker configuration
│   ├── nginx.conf            Nginx config (deployed to host OS)
│   ├── config/               Django project config (settings, urls, celery, wsgi)
│   ├── accounts/             Authentication — signup, login, logout
│   ├── uploads/              File management — CSV/FASTQ/FASTA, async MD5 verification
│   ├── projects/             Pipeline orchestration — ProjectRun model + Celery tasks
│   ├── dashboard/            User dashboard view (Django template)
│   ├── api/v1/               DRF REST API (accounts, uploads, projects)
│   ├── drc_timepoint/        First analysis pipeline (optimal timepoint for DRC modelling)
│   ├── hpc_services/         SSH/SFTP/SLURM utilities for Rocket HPC (USE_HPC=True to enable)
│   └── hpc_jobs/             Scripts deployed to Rocket cluster (run_analysis.py, submit_drc.sh)
└── frontend/                 React 19 + Vite (in development, replacing Django templates)
    └── src/
        └── components/       Header, Homepage, Login, Signup, Dashboard, Footer
```

## Future Roadmap (priority order)

1. **API tests** — endpoints currently tested manually via Postman; write pytest suite for `api/v1` before the React migration
2. **React frontend** — complete the React SPA and retire Django templates, consuming the existing API
