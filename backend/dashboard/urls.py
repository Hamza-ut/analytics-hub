from . import views
from django.urls import path

# defining namespace means templates should be referenced with this namespace, e.g. dashboard:delete_file
app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("delete_file/<int:file_id>/", views.delete_file_view, name="delete_file"),
    path("delete_project/<int:project_id>/", views.delete_project_view, name="delete_project"),
    path("download/<int:file_id>/", views.download_file_view, name="download_file"),
]
