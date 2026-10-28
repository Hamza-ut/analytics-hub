from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.Login.as_view(), name="login"),
    path("sso-login/", views.SSOLogin.as_view(), name="sso_login"),
    path("callback/", views.SSOCallback.as_view(), name="sso_callback"),
]
