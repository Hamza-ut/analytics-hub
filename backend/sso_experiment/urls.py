from django.urls import path
from . import views

app_name = "sso_experiment"

urlpatterns = [
    path("simple_session/", views.simple_session, name="simple_session"),
    path("simple_oidc/", views.simple_oidc, name="simple_oidc"),
    path("simple_redirect/", views.simple_redirect_page, name="redirect_page"),
    path("simple_callback/", views.simple_callback, name="simple_callback"),
    path("simple_logout/", views.generic_logout, name="logout"),
]
