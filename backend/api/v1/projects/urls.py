from django.urls import path, include
from . import views

urlpatterns = [
    # 1. To Create: POST /api/v1/projects/create/
    path(
        "create/",
        views.project_create,
        name="project-create",
    ),
    # 2. To Run: POST /api/v1/projects/PRJ_XXXXXX/run/
    path("run/<str:project_id>/", views.project_run, name="project-run"),
    # 3. To Get Results: GET /api/v1/projects/PRJ_XXXXXX/results/
    path("results/<str:project_id>/", views.project_result, name="project-results"),
    # 4. To Delete Project: POST /api/v1/projects/PRJ_XXXXXX/delete/
    path("project/<str:project_id>/", views.project_detail, name="project-detail"),
    # 5. To List Projects: GET /api/v1/projects/all/
    path("all/", views.projects_list, name="project-list"),
    # 6. To List Available Pipelines: GET /api/v1/projects/pipelines/
    path("pipelines/", views.pipelines_list, name="pipeline-list"),
]
