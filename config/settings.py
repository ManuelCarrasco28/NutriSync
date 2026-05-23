"""
Django settings for NutriSync — Plataforma de Gestión Profesional para Nutricionistas.
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ─── Seguridad ────────────────────────────────────────────────────────────────

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-+cf^9q!ws)x$@j*a5d0w@j@f(7l9o^dvuoh7b-+)jieg_!c+8d",
)

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0",
    cast=lambda v: [s.strip() for s in v.split(",")],
)


# ─── Apps instaladas ──────────────────────────────────────────────────────────

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto NutriSync — orden según dependencias
    "core.apps.CoreConfig",  # Auth, dashboard, perfil del nutricionista (CoreConfig para signals)
    "pacientes",  # Gestión de pacientes
    "citas",  # Agenda de citas
    "nutricion",  # Base de alimentos y planes nutricionales
    "seguimiento",  # Medidas corporales y notas clínicas
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.ThreadLocalRequestMiddleware",  # Permite acceder al request/usuario actual de forma global en modelos y formularios (ThreadLocal)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Inyecta el PerfilNutricionista en todos los templates
                # para que el sidebar y el header tengan acceso al nombre/especialidad
                "core.context_processors.perfil_nutricionista",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ─── Autenticación ────────────────────────────────────────────────────────────

# Redirige al login si el usuario no está autenticado (@login_required)
LOGIN_URL = "/login/"
# Tras un login exitoso, va al dashboard
LOGIN_REDIRECT_URL = "/"
# Tras logout, vuelve al login
LOGOUT_REDIRECT_URL = "/login/"


# ─── Base de datos ────────────────────────────────────────────────────────────

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("DB_NAME", default="nutrisync_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        # DB_HOST=db con Docker; DB_HOST=localhost sin Docker
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}


# ─── Validación de contraseñas ────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─── Internacionalización ─────────────────────────────────────────────────────

# Español para que el admin, mensajes de validación y errores estén en español
LANGUAGE_CODE = "es"

TIME_ZONE = "America/Lima"

USE_I18N = True
USE_TZ = True


# ─── Archivos estáticos ───────────────────────────────────────────────────────

STATIC_URL = "/static/"

# Directorio donde colocaremos nuestros estilos manuales (CSS personalizado, Tailwind, etc.)
STATICFILES_DIRS = [BASE_DIR / "static"]

# Directorio donde Django recopilará los estáticos (ej. panel de admin) usando collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"


# ─── Otros ────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
