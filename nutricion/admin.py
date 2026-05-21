# nutricion/admin.py
# Registro de modelos de nutrición en el panel de administración.
# ComidaPlan se registra como inline de PlanNutricional para edición integrada.

from django.contrib import admin
from .models import Alimento, PlanNutricional, ComidaPlan


# ─── Inline de comidas dentro del plan ───────────────────────────────────────

class ComidaPlanInline(admin.TabularInline):
    """
    Inline de ComidaPlan dentro de PlanNutricional.
    Permite agregar/editar comidas directamente desde el plan en el admin.
    """
    model = ComidaPlan
    extra = 1
    fields = ("dia_semana", "tipo_comida", "descripcion", "calorias_estimadas", "alimentos_sugeridos")
    # filter_horizontal facilita la selección de alimentos en el ManyToMany
    filter_horizontal = ("alimentos_sugeridos",)


# ─── Alimento ─────────────────────────────────────────────────────────────────

@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    """
    Administración del catálogo de alimentos.
    Permite buscar, filtrar por categoría y ordenar por nombre.
    """
    list_display = ("nombre", "categoria", "calorias_100g", "proteinas_100g",
                    "carbohidratos_100g", "grasas_100g", "estado", "fecha_registro")
    list_filter = ("categoria", "estado")
    search_fields = ("nombre",)
    list_editable = ("estado",)
    ordering = ("nombre",)
    fieldsets = (
        ("Información general", {
            "fields": ("nombre", "categoria", "porcion_referencia", "estado")
        }),
        ("Valores nutricionales por 100g", {
            "fields": ("calorias_100g", "proteinas_100g", "carbohidratos_100g", "grasas_100g", "fibra_100g"),
            "description": "Todos los valores son por cada 100 gramos del alimento.",
        }),
    )


# ─── PlanNutricional ──────────────────────────────────────────────────────────

@admin.register(PlanNutricional)
class PlanNutricionalAdmin(admin.ModelAdmin):
    """
    Administración de planes nutricionales con inline de comidas.
    Se muestra el paciente, objetivo, estado y fecha de creación en la lista.
    """
    list_display = ("nombre", "paciente", "objetivo", "calorias_diarias", "estado", "fecha_creacion")
    list_filter = ("estado", "objetivo", "fecha_creacion")
    search_fields = ("nombre", "paciente__nombre", "paciente__apellido")
    # select_related evita N+1 queries al mostrar el nombre del paciente en la lista
    list_select_related = ("paciente",)
    ordering = ("-fecha_creacion",)
    inlines = [ComidaPlanInline]
    fieldsets = (
        ("Información del plan", {
            "fields": ("paciente", "nombre", "objetivo", "estado")
        }),
        ("Fechas", {
            "fields": ("fecha_inicio", "fecha_fin"),
        }),
        ("Macronutrientes objetivo", {
            "fields": ("calorias_diarias", "proteinas_g", "carbohidratos_g", "grasas_g"),
            "description": "Valores diarios objetivo para el paciente.",
        }),
        ("Observaciones", {
            "fields": ("observaciones",),
            "classes": ("collapse",),
        }),
    )


# ─── ComidaPlan (administración independiente) ───────────────────────────────

@admin.register(ComidaPlan)
class ComidaPlanAdmin(admin.ModelAdmin):
    """
    Administración independiente de comidas del plan.
    También accesible desde el inline en PlanNutricionalAdmin.
    """
    list_display = ("__str__", "plan", "dia_semana", "tipo_comida", "calorias_estimadas")
    list_filter = ("dia_semana", "tipo_comida")
    search_fields = ("plan__nombre", "plan__paciente__nombre")
    # select_related evita N+1 al mostrar el plan y paciente en la lista
    list_select_related = ("plan", "plan__paciente")
    filter_horizontal = ("alimentos_sugeridos",)
