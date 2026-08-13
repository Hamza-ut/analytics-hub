from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.Signup.as_view(), name="signup"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("user/", views.UserDetail.as_view(), name="userdetail"),
]
