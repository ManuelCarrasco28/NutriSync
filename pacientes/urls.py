# pacientes/urls.py
# URLs de la app pacientes. Namespace 'pacientes' para referenciar desde templates.

from django.urls import path
from . import views

app_name = "pacientes"

urlpatterns = [
    path("", views.PacienteListView.as_view(), name="lista"),
    path("nuevo/", views.PacienteCreateView.as_view(), name="nuevo"),
    path("<int:pk>/", views.PacienteDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.PacienteUpdateView.as_view(), name="editar"),
    path("<int:pk>/toggle/", views.paciente_toggle_estado, name="toggle"),
]
