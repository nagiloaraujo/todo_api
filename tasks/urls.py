"""Rotas do app: o cadastro, o login e o CRUD das tarefas."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, RegisterView, TaskViewSet

# O router cria as rotas de CRUD automaticamente:
#   GET/POST              /api/tasks/
#   GET/PUT/PATCH/DELETE  /api/tasks/<id>/
router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    # Cadastro e login vêm primeiro por serem endereços fixos.
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),

    # Depois as rotas criadas pelo router (/api/tasks/...).
    path("", include(router.urls)),
]
