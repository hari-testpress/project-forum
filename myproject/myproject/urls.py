from django.contrib import admin
from django.urls import path, include
from boards import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("boards/", include("boards.urls", namespace="board")),
]
