"""
Configurações do projeto API de Tarefas (TO-DO).

Este é o painel central do Django: aqui dizemos quais bibliotecas usamos,
qual banco de dados, como a autenticação funciona, etc.

O projeto foi pensado para ser simples de ler: um único app ("tasks"), banco
SQLite (um arquivo no computador, sem instalar nada) e poucos ajustes.

O mesmo arquivo serve para os dois ambientes:
- LOCAL (aula): roda no computador, com SQLite, sem configurar nada.
- NUVEM (Render): as diferenças chegam por variáveis de ambiente
  (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL), então nenhum segredo
  ou endereço fica escrito no código.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url

# Caminho base do projeto (a pasta que contém o manage.py).
BASE_DIR = Path(__file__).resolve().parent.parent


def lista_do_ambiente(nome, padrao=""):
    """Lê uma variável de ambiente com vários valores separados por vírgula."""
    return [item.strip() for item in os.environ.get(nome, padrao).split(",") if item.strip()]


# ----------------------------------------------------------------------
# Segurança
# ----------------------------------------------------------------------
# Esta chave assina os tokens e as sessões. Em produção ela vem de uma
# variável de ambiente; em sala, deixamos um valor fixo para simplificar.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-troque-esta-chave-em-producao-todo-api",
)

# DEBUG=True mostra os erros detalhados na tela, o que ajuda muito na aula.
# No Render ele fica desligado (a variável DJANGO_DEBUG é definida lá).
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# O "*" libera o acesso por qualquer endereço. É cômodo na sala: o aluno
# pode abrir do celular na mesma rede, por exemplo.
ALLOWED_HOSTS = lista_do_ambiente("DJANGO_ALLOWED_HOSTS", "*")

# Endereços confiáveis para os formulários (usados pelo /admin/ e pela
# interface navegável da API). Precisam vir com "https://" na frente.
CSRF_TRUSTED_ORIGINS = lista_do_ambiente("DJANGO_CSRF_TRUSTED_ORIGINS")

# O Render avisa ao Django qual é o endereço público do serviço, então a
# API publicada funciona sem escrevermos esse endereço no código.
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
if os.environ.get("RENDER_EXTERNAL_URL"):
    CSRF_TRUSTED_ORIGINS.append(os.environ["RENDER_EXTERNAL_URL"])

# Com o DEBUG desligado (produção), confiamos no cabeçalho do proxy do
# Render para saber que a conexão chegou por HTTPS.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# ----------------------------------------------------------------------
# Aplicativos instalados
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    # Apps internos do Django (admin, autenticação, sessões...)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Bibliotecas de terceiros
    "rest_framework",            # Django REST Framework (a API)
    "rest_framework_simplejwt",  # gera o token devolvido no login
    "corsheaders",               # libera o front-end a falar com a API
    "drf_spectacular",           # documentação automática (Swagger)

    # O nosso app: guarda o modelo Task, o cadastro/login e o CRUD.
    "tasks",
]


# ----------------------------------------------------------------------
# Middlewares (as "camadas" por onde cada requisição passa)
# ----------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve o CSS/imagens do /admin/ e do Swagger também na nuvem (no Render
    # não existe o "runserver" para fazer isso).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Precisa vir antes do CommonMiddleware para tratar o CORS corretamente.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "todo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "todo.wsgi.application"


# ----------------------------------------------------------------------
# Banco de dados
# ----------------------------------------------------------------------
# SQLite cria um arquivo (db.sqlite3) na pasta do projeto. Não é preciso
# instalar nem configurar nada — perfeito para a aula.
# Se existir a variável DATABASE_URL (ex: no Render, apontando para um
# PostgreSQL), ela manda. Assim trocar de banco não exige mexer no código.
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ----------------------------------------------------------------------
# Validação de senha (usada pelo "createsuperuser" e pelo /admin/)
# ----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ----------------------------------------------------------------------
# Idioma, fuso horário e arquivos estáticos
# ----------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Bahia"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# Pasta onde o "collectstatic" junta todo o CSS/JS (do admin e do Swagger)
# antes de publicar. No Render ela é gerada no momento do build.
STATIC_ROOT = BASE_DIR / "staticfiles"

# O whitenoise comprime esses arquivos e cuida do cache, deixando o /admin/
# e a documentação mais rápidos na nuvem.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ----------------------------------------------------------------------
# CORS: quem pode chamar a API pelo navegador
# ----------------------------------------------------------------------
# Liberamos todos os endereços para facilitar a aula: o front-end do aluno
# pode rodar em qualquer porta (5500, 5173, 3000...). Em um sistema de
# verdade, aqui ficaria a lista dos domínios permitidos.
CORS_ALLOW_ALL_ORIGINS = True


# ----------------------------------------------------------------------
# Django REST Framework
# ----------------------------------------------------------------------
REST_FRAMEWORK = {
    # Como o usuário se identifica: pelo token enviado no cabeçalho
    # "Authorization: Bearer <token>".
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # Por padrão, todo endpoint exige login. Quem for público (cadastro e
    # login) avisa isso na própria view.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Biblioteca que gera a documentação OpenAPI.
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# ----------------------------------------------------------------------
# Token do login (SimpleJWT)
# ----------------------------------------------------------------------
SIMPLE_JWT = {
    # O token vale 30 dias. O aluno faz o login uma única vez, o front-end
    # guarda esse valor no localStorage e não precisa logar de novo.
    # Repare que não configuramos "refresh": esta API é simplificada de
    # propósito e não tem o fluxo de renovação de token.
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    # Como o token chega no cabeçalho: Authorization: Bearer <token>
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ----------------------------------------------------------------------
# Documentação automática (Swagger / ReDoc)
# ----------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "API de Tarefas (TO-DO)",
    "DESCRIPTION": (
        "API simples de lista de tarefas, criada para a avaliação final da turma.\n\n"
        "**Como testar:** faça o login em `POST /api/login/`, copie o valor de "
        "`token` da resposta e clique no botão **Authorize** (o cadeado no topo "
        "da página). Depois é só usar os endpoints de tarefas."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
