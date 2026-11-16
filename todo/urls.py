"""
As rotas principais do projeto.

É aqui que ligamos cada endereço da API a uma view. Repare como fica fácil
de ler: tudo o que é da API começa com "api/".
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Interface de administração do Django (útil para conferir os dados).
    path("admin/", admin.site.urls),

    # Nossas rotas: /api/register/, /api/login/ e /api/tasks/...
    path("api/", include("tasks.urls")),

    # Documentação automática gerada a partir do código.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
