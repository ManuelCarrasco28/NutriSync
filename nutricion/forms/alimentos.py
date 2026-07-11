from django import forms
from django.core.exceptions import ValidationError
from ..models import Alimento

INPUT_CLASSES = (
    "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent "
    "transition-all duration-200"
)
SELECT_CLASSES = INPUT_CLASSES

class AlimentoForm(forms.ModelForm):
    """Formulario para crear y editar alimentos del catálogo nutricional."""

    class Meta:
        model = Alimento
        fields = [
            "nombre", "categoria", "porcion_referencia",
            "calorias_100g", "proteinas_100g", "carbohidratos_100g",
            "grasas_100g", "fibra_100g", "estado",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Ej: Arroz blanco cocido",
            }),
            "categoria": forms.Select(attrs={"class": SELECT_CLASSES}),
            "porcion_referencia": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Ej: 1 taza (240g)",
            }),
            "calorias_100g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.01", "min": "0",
            }),
            "proteinas_100g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.01", "min": "0",
            }),
            "carbohidratos_100g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.01", "min": "0",
            }),
            "grasas_100g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.01", "min": "0",
            }),
            "fibra_100g": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "step": "0.01", "min": "0",
            }),
        }
        labels = {
            "calorias_100g": "Calorías (kcal/100g)",
            "proteinas_100g": "Proteínas (g/100g)",
            "carbohidratos_100g": "Carbohidratos (g/100g)",
            "grasas_100g": "Grasas (g/100g)",
            "fibra_100g": "Fibra (g/100g)",
        }

    def clean_nombre(self):
        """Normalizamos el nombre para evitar duplicados por mayúsculas/minúsculas."""
        nombre = self.cleaned_data.get("nombre", "").strip()
        qs = Alimento.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(
                f"Ya existe un alimento con el nombre «{nombre}». "
                "Verifica el catálogo antes de agregar uno nuevo."
            )
        return nombre
