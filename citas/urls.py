# citas/urls.py
# Rutas locales para el módulo de agenda de citas.

from django.urls import path
from . import views

app_name = "citas"

urlpatterns = [
    path("agenda/", views.AgendaView.as_view(), name="agenda"),
    path("citas/nueva/", views.CitaCreateView.as_view(), name="nueva"),
    path("citas/<int:pk>/", views.CitaDetailView.as_view(), name="detalle"),
    path("citas/<int:pk>/editar/", views.CitaUpdateView.as_view(), name="editar"),
    path("citas/<int:pk>/estado/", views.cita_cambiar_estado, name="cambiar_estado"),
]
