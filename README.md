# analytics-hub

Internal analysis platform for the Bioengineering Department at the University of Tartu (EU-funded biofoundry project, [digibio.ut.ee](https://digibio.ut.ee)).

The platform provides a workflow interface for running bioinformatics analyses, managing research data files, and submitting compute jobs to the university HPC cluster (Rocket). It is designed to host multiple analysis workflows — the first implemented is **DRC Optimal Timepoint**, a tool for identifying the optimal measurement window in dose-response curve experiments.

---

## Current State

- **Backend** — Django + DRF REST API is complete. All endpoints are functional and tested.
- **Frontend** — React SPA is in active development. It runs outside Docker (see [Running the Frontend](#running-the-frontend)) and is not yet production-ready.
- **HPC integration** — Executor abstraction is in place. Local (Celery) execution is active. HPC (Rocket/SLURM) execution is scaffolded and will be enabled in a future milestone.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Django REST Framework 3.17 |
| Database | PostgreSQL |
| Task queue | Celery 5.6 + Redis |
| Analysis engine | pandas, numpy, scikit-learn, scipy |
| HPC (planned) | Paramiko 5.0 → Rocket cluster (SLURM) |
| Application server | Gunicorn |
| Reverse proxy | Nginx |
| Containerisation | Docker, docker-compose |
| Frontend | React 19, Vite, Axios |

---

## Project Structure

```
analytics-hub/
├── docker-compose.yml
├── backend/
│   ├── config/               Django project config (settings, urls, celery, wsgi)
│   ├── accounts/             Django auth app (User model)
│   ├── projects/             Project + Workflow models and Celery tasks
│   ├── uploads/              File management — upload, MD5 verification, deletion
│   ├── workflows/
│   │   └── timepoint/        DRC Optimal Timepoint analysis engine + models + tasks
│   ├── executors/            Executor abstraction layer
│   │   ├── base.py           Abstract BaseExecutor interface
│   │   ├── factory.py        Returns the right executor based on EXECUTOR_BACKEND setting
│   │   ├── local/            LocalServerExecutor — dispatches Celery tasks
│   │   └── hpc/              HPCExecutor — scaffolded, not yet active
│   ├── external_tools/       Standalone analysis engine packages (drc_timepoint engine)
│   ├── api/
│   │   └── v1/               DRF REST API
│   │       ├── accounts/     Auth endpoints
│   │       ├── uploads/      File endpoints
│   │       ├── projects/     Project + workflow endpoints
│   │       └── workflows/
│   │           └── timepoint/ Timepoint-specific config, execute, results endpoints
│   ├── Dockerfile
│   ├── entrypoint.sh         migrate + collectstatic + start Gunicorn
│   ├── gunicorn.conf.py
│   ├── nginx.conf            Nginx config for host OS deployment
│   └── requirements.txt
└── frontend/                 React 19 + Vite (in active development)
    └── src/
        ├── api/              Axios API modules per domain
        ├── components/       Shared UI components + workflow-specific components
        ├── contexts/         AuthContext (token + user state)
        ├── pages/            Route-level page components
        └── utils/
```

---

## Getting Started

### Backend (Docker — recommended)

```bash
docker-compose up --build
```

This starts:
- `backend` — Django dev server on port 8000
- `celery` — Celery worker with auto-restart on code changes
- `db` — PostgreSQL on `127.0.0.1:5433` (host-accessible for tools like DBeaver)
- `inmemorydb` — Redis

On first run, `entrypoint.sh` runs automatically: applies migrations, creates the superuser from env vars, and seeds the Workflow table if empty.

**Environment:**
```bash
cp backend/.env.example backend/.env
# Fill in SECRET_KEY, DB credentials, and optionally SLACK_WEBHOOK_URL
```

### Running the Frontend

The frontend runs outside Docker during development:

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server runs on `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

---

## API Reference

All endpoints are prefixed with `/api/v1/`. Authentication uses DRF Token Authentication — include `Authorization: Token <token>` on all protected routes.

### Accounts

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/accounts/signup/` | No | Register a new user |
| POST | `/accounts/login/` | No | Obtain auth token |
| POST | `/accounts/logout/` | Yes | Invalidate auth token |
| GET | `/accounts/user/` | Yes | Get authenticated user details |

### Uploads

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/uploads/file/` | Yes | Upload a file (CSV/FASTQ/FASTA, max 10 GB) |
| GET | `/uploads/file/<upload_id>/` | Yes | Get file metadata |
| DELETE | `/uploads/file/<upload_id>/` | Yes | Delete a file (blocked if used by a project) |
| GET | `/uploads/file/<upload_id>/download/` | Yes | Download the file |
| GET | `/uploads/all/` | Yes | List all files for the authenticated user |
| GET | `/uploads/stats/` | Yes | Storage usage stats |

Files go through async MD5 verification via Celery after upload. Status progresses `UPLOADING → UPLOADED` (or `FAILED`). Only `UPLOADED` files can be attached to a project.

### Projects

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/projects/workflows/` | Yes | List available workflows |
| POST | `/projects/create/` | Yes | Create a project (specify workflow by name) |
| GET | `/projects/all/` | Yes | List projects for the authenticated user |
| GET | `/projects/project/<project_id>/` | Yes | Get project details |
| DELETE | `/projects/project/<project_id>/` | Yes | Delete a project (cascades Run and Result) |

**Create project request body:**
```json
{ "workflow": "drctimepoint" }
```

Project status lifecycle: `CREATED → QUEUED → RUNNING → SUCCESS / FAILED`

### Workflow: DRC Optimal Timepoint (`w1`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/workflows/timepoint/config/<project_id>/` | Yes | Attach timepoint configuration to a project |
| GET | `/workflows/timepoint/config/<project_id>/` | Yes | Retrieve current configuration |
| POST | `/workflows/timepoint/execute/<project_id>/` | Yes | Queue the analysis |
| GET | `/workflows/timepoint/results/<project_id>/` | Yes | Retrieve analysis results |

**Configure request body:**
```json
{
  "file": "upl_abc123",
  "group_fields": ["Condition", "Ratio"],
  "dose_field": "XMIC",
  "od_field": "Raw_od",
  "time_field": "hour",
  "top_n": 2
}
```

**Typical workflow sequence:**
1. Upload a file → `POST /uploads/file/`
2. Wait for status `UPLOADED` → `GET /uploads/file/<upload_id>/`
3. Create a project → `POST /projects/create/`
4. Attach config → `POST /workflows/timepoint/config/<project_id>/`
5. Execute → `POST /workflows/timepoint/execute/<project_id>/`
6. Poll status → `GET /projects/project/<project_id>/`
7. Fetch results → `GET /workflows/timepoint/results/<project_id>/`

---

## Executor Architecture

The platform uses an executor abstraction to decouple workflow execution from the underlying compute layer:

```
EXECUTOR_BACKEND=localserver  →  LocalServerExecutor  →  Celery task
EXECUTOR_BACKEND=hpc          →  HPCExecutor           →  Rocket/SLURM (planned)
```

Set `EXECUTOR_BACKEND` in `.env` to switch backends. The rest of the application is unaffected.

---

## Roadmap

1. **React frontend** — complete the SPA (currently in development, running outside Docker)
2. **HPC integration** — implement `HPCExecutor` to submit jobs to Rocket cluster via Paramiko + SLURM
3. **Frontend in Docker** — add the React build to `docker-compose.yml` once the SPA is stable
4. **Additional workflows** — Strain QC (`w2`) and further pipelines from the biofoundry team
