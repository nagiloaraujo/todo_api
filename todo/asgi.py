"""Ponto de entrada assíncrono. Não usamos nesta aula, mas o Django já deixa pronto."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")

application = get_asgi_application()
