from django.urls import path
from . import views

app_name = "sso_experiment"

urlpatterns = [
    path("login/", views.session_based, name="session_based"),
    path("login/oidc/", views.oidc_based, name="oidc_based"),
    path("simple_redirect/", views.simple_redirect_page, name="redirect_page"),
    path("oidc/callback/", views.oidc_callback, name="oidc_callback"),
]
