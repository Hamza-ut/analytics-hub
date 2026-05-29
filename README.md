# analytics-hub

Biofoundry analysis platform for the Bioengineering Department at the University of Tartu.

## About

analytics-hub is the internal web platform for EU-funded biofoundry project. It provides a pipeline interface for running bioinformatics analyses, managing research data files, and submitting compute jobs to the university HPC cluster.

The platform is designed to host multiple analysis pipelines. The first pipeline currently implemented is **drc_timepoint**, a small tool for identifying optimal timepoint for DRC modelling.
It's not a compute heavy tool so some sleep time added for it to mimic the slow compute heavy pipeline.
Actual compute heavy workflows by Marko will come here later

## Current State

The REST API is complete and functional but the frontend is currently in active development — for now the platform uses Django HTML templates for the UI and non api based views for backend. The React frontend (`frontend/`) is being built in parallel and will replace the templates once ready.

## Tech Stack

| Layer                     | Technology                             |
| ------------------------- | -------------------------------------- |
| Backend                   | Django 4.2, Django REST Framework 3.17 |
| Database                  | PostgreSQL                             |
| Task queue                | Celery 5.6 + Redis                     |
| Analysis engine           | pandas, numpy, scikit-learn            |
| Frontend (current)        | Django HTML templates                  |
| Frontend (in development) | React 19, Vite, Axios                  |

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (running and accessible)
- Redis (running on localhost:6379)

## Getting Started

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in DB credentials and secret key
python manage.py migrate
python manage.py runserver
```

The backend will be available at `http://localhost:8000`.

### 2. Celery Worker

In a separate terminal:

```bash
cd backend
source .venv/bin/activate
python -m celery -A config worker -l info
```

Redis must be running before starting the worker.

### 3. Frontend (React dev server)

```bash
cd frontend
npm install
npm run dev
```

The React dev server will be available at `http://localhost:5173`.

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
├── backend/
│   ├── config/           Django project config (settings, urls, celery, wsgi)
│   ├── accounts/         Authentication — signup, login, logout
│   ├── uploads/          File management — CSV/FASTQ/FASTA, async MD5 verification
│   ├── projects/         Pipeline orchestration — ProjectRun model + Celery tasks
│   ├── dashboard/        User dashboard view
│   ├── api/v1/           DRF REST API (accounts, uploads, projects)
│   └── drc_timepoint/    First analysis pipeline (optimal timepoint identifier for DRC modelling)
└── frontend/             React 19 + Vite (in development, replacing Django templates)
    └── src/
        └── components/   Header, Homepage, Login, Signup, Dashboard, Footer
```

## Future Roadmap (priority order)

1. **HPC computation** — route heavy pipelines to the Rocket cluster (SLURM) via SSH/SFTP instead of running locally on Celery
2. **Nginx + Gunicorn** — learn the production serving stack: Gunicorn replaces `manage.py runserver`, Nginx sits in front as a reverse proxy handling HTTPS and static files.
3. **Dockerization** — containerize all services (Django + Gunicorn + Nginx + Celery + Redis + PostgreSQL) into a docker-compose setup so UT IT can deploy via Kubernetes
4. **API tests** — endpoints currently tested manually via Postman; write pytest suite for `api/v1` before the React migration
5. **React frontend** — complete the React SPA and retire Django templates, consuming the existing API
