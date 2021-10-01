from django.urls import path
from django.contrib.auth import views as auth_view

from . import views

app_name = "account"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("logout/", auth_view.LogoutView.as_view(), name="logout"),
    path(
        "login/",
        auth_view.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
]
