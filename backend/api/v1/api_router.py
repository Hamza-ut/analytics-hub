from django.urls import path, include

urlpatterns = [
    path("accounts/", include("api.v1.accounts.urls")),
    path("uploads/", include("api.v1.uploads.urls")),
    path("projects/", include("api.v1.projects.urls")),
    path("workflows/timepoint/", include("api.v1.workflows.timepoint.urls")),
]
