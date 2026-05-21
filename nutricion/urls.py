# nutricion/urls.py
# URLs del módulo de planes nutricionales y catálogo de alimentos.
# Namespace: 'nutricion'

from django.urls import path
from . import views

app_name = "nutricion"

urlpatterns = [
    # ─── Catálogo de alimentos ─────────────────────────────────────────────
    path("alimentos/", views.AlimentoListView.as_view(), name="alimentos"),
    path("alimentos/nuevo/", views.AlimentoCreateView.as_view(), name="alimento_nuevo"),
    path("alimentos/<int:pk>/editar/", views.AlimentoUpdateView.as_view(), name="alimento_editar"),
    path("alimentos/cargar-ejemplos/", views.cargar_alimentos_ejemplo, name="cargar_ejemplos"),

    # ─── Planes nutricionales ──────────────────────────────────────────────
    path("planes/", views.PlanListView.as_view(), name="planes"),
    path("planes/nuevo/<int:paciente_pk>/", views.PlanCreateView.as_view(), name="plan_nuevo"),
    path("planes/<int:pk>/", views.PlanDetailView.as_view(), name="plan_detalle"),
    path("planes/<int:pk>/editar/", views.PlanUpdateView.as_view(), name="plan_editar"),
    path("planes/<int:pk>/toggle/", views.plan_toggle_estado, name="plan_toggle"),

    # ─── Comidas del plan ──────────────────────────────────────────────────
    path("planes/<int:plan_pk>/comidas/nueva/", views.comida_crear, name="comida_nueva"),
    path("comidas/<int:pk>/eliminar/", views.comida_eliminar, name="comida_eliminar"),
]
