from django.urls import path
from . import views

urlpatterns = [
    path("file/", views.Upload.as_view(), name="upload-file"),
    path("file/<str:upload_id>/", views.FileDetail.as_view(), name="file-detail"),
    path("file/<str:upload_id>/download/", views.FileDownload.as_view(), name="file-download"),
    path("all/", views.FilesList.as_view(), name="files-list"),
    path("stats/", views.FileStats.as_view(), name="upload-stats"),
]
