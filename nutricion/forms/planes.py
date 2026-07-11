from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from ..models import PlanNutricional, ComidaPlan, Alimento, Receta
from config.choices import DiaSemana, TipoComida, Objetivo

INPUT_CLASSES = (
    "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent "
    "transition-all duration-200"
)
SELECT_CLASSES = INPUT_CLASSES
TEXTAREA_CLASSES = INPUT_CLASSES + " resize-none"

class PlanNutricionalForm(forms.ModelForm):
    """
    Formulario para crear y editar un plan nutricional.
    La validación de 'un solo plan activo por paciente' se hace en clean()
    para que funcione tanto en el form web como en el admin de Django.
    """

    class Meta:
        model = PlanNutricional
        fields = [
            "nombre", "objetivo", "fecha_inicio", "fecha_fin",
            "calorias_diarias", "proteinas_g", "carbohidratos_g", "grasas_g",
            "observaciones", "estado",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Ej: Plan pérdida de peso — Enero 2025",
            }),
            "objetivo": forms.Select(attrs={"class": SELECT_CLASSES}),
            "fecha_inicio": forms.DateInput(
                attrs={"class": INPUT_CLASSES, "type": "date"},
                format="%Y-%m-%d",
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": INPUT_CLASSES, "type": "date"},
                format="%Y-%m-%d",
            ),
            "calorias_diarias": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "min": "500",
            }),
            "proteinas_g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.1", "min": "0",
            }),
            "carbohidratos_g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.1", "min": "0",
            }),
            "grasas_g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.1", "min": "0",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": TEXTAREA_CLASSES, "rows": 3,
                "placeholder": "Indicaciones adicionales, restricciones, observaciones clínicas...",
            }),
        }

    def __init__(self, *args, **kwargs):
        self.paciente = kwargs.pop("paciente", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")
        estado = cleaned_data.get("estado")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio del plan."
            )

        if estado and self.paciente:
            planes_activos = PlanNutricional.objects.filter(
                paciente=self.paciente, estado=True
            )
            if self.instance.pk:
                planes_activos = planes_activos.exclude(pk=self.instance.pk)
            if planes_activos.exists():
                raise ValidationError(
                    "Este paciente ya tiene un plan nutricional activo. "
                    "Desactiva el plan actual antes de crear uno nuevo."
                )

        return cleaned_data


class ComidaPlanForm(forms.ModelForm):
    """Formulario para agregar o editar una comida dentro de un plan nutricional."""

    class Meta:
        model = ComidaPlan
        fields = [
            "dia_semana", "tipo_comida", "descripcion",
            "alimentos_sugeridos", "recetas_sugeridas", "calorias_estimadas",
        ]
        widgets = {
            "dia_semana": forms.Select(attrs={"class": SELECT_CLASSES}),
            "tipo_comida": forms.Select(attrs={"class": SELECT_CLASSES}),
            "descripcion": forms.Textarea(attrs={
                "class": TEXTAREA_CLASSES, "rows": 3,
                "placeholder": "Ej: Avena con frutas y miel, vaso de leche descremada",
            }),
            "alimentos_sugeridos": forms.CheckboxSelectMultiple(),
            "recetas_sugeridas": forms.CheckboxSelectMultiple(),
            "calorias_estimadas": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "min": "0",
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        plan = kwargs.pop("plan", None)
        super().__init__(*args, **kwargs)
        if plan:
            self.plan = plan

        self.fields["alimentos_sugeridos"].queryset = (
            Alimento.objects.filter(estado=True).order_by("nombre")
        )
        
        if user:
            self.fields["recetas_sugeridas"].queryset = (
                Receta.objects.filter(Q(es_sistema=True) | Q(creado_por=user)).order_by("nombre")
            )
        else:
            self.fields["recetas_sugeridas"].queryset = (
                Receta.objects.filter(es_sistema=True).order_by("nombre")
            )

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get("dia_semana")
        tipo = cleaned_data.get("tipo_comida")

        if dia and tipo and hasattr(self, "plan"):
            qs = ComidaPlan.objects.filter(plan=self.plan, dia_semana=dia, tipo_comida=tipo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f"Ya existe una entrada de {dict(TipoComida.CHOICES).get(tipo, tipo)} "
                    f"para el {dict(DiaSemana.CHOICES).get(dia, dia)} en este plan."
                )
        return cleaned_data
