# administracion/apps.py

from django.apps import AppConfig


class AdministracionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "administracion"
    verbose_name = "Panel de Administración"
