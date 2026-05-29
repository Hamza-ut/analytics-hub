from . import views
from django.urls import path

app_name = "uploads"

urlpatterns = [
    path("file/", views.upload_view, name="upload"),
]
