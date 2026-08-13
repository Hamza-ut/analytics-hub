from django.urls import path
from . import views

urlpatterns = [
    path("workflows/", views.WorkflowList.as_view(), name="workflows"),
    path("create/", views.CreateProject.as_view(), name="create_project"),
    path(
        "project/<str:project_id>/",
        views.ProjectDetail.as_view(),
        name="project-detail",
    ),
    path("all/", views.ProjectsList.as_view(), name="project-list"),
]
