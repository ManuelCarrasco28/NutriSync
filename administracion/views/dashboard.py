# administracion/views/dashboard.py
# Vista del dashboard del administrador.

from django.shortcuts import render
from administracion.mixins import admin_requerido


@admin_requerido
def dashboard_view(request):
    """Vista principal del panel de administración."""
    return render(request, "administracion/dashboard/index.html")

