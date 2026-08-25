from django.urls import path
from . import views

urlpatterns = [
    path("config/<str:project_id>/", views.RunConfigure.as_view(), name="strainqc-config"),
    path("execute/<str:project_id>/", views.RunExecute.as_view(), name="strainqc-execute"),
    path("results/<str:project_id>/", views.RunResults.as_view(), name="strainqc-results"),
]
