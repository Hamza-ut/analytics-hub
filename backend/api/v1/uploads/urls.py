from django.urls import path
from . import views

urlpatterns = [
    path("file/", views.upload, name="upload-file"),
    path("file/<str:upload_id>/", views.file_detail, name="file-detail"),
    path("file/<str:upload_id>/download/", views.file_detail, name="download-file"),
    path("all/", views.files_list, name="files-list"),
    path("stats/", views.upload_stats, name="upload-stats"),
]
