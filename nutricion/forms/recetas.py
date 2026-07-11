from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from ..models import Receta, IngredienteReceta, Alimento

INPUT_CLASSES = (
    "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent "
    "transition-all duration-200"
)
SELECT_CLASSES = INPUT_CLASSES
TEXTAREA_CLASSES = INPUT_CLASSES + " resize-none"

class RecetaForm(forms.ModelForm):
    """Formulario para crear y editar recetas (datos básicos)."""

    class Meta:
        model = Receta
        fields = ["nombre", "descripcion", "tiempo_preparacion", "porciones", "imagen_predeterminada"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Ej: Ensalada César Saludable",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": TEXTAREA_CLASSES,
                "rows": 2,
                "placeholder": "Breve descripción de la receta (opcional)...",
            }),
            "tiempo_preparacion": forms.NumberInput(attrs={
                "class": INPUT_CLASSES,
                "min": "1",
                "max": "480",
            }),
            "porciones": forms.NumberInput(attrs={
                "class": INPUT_CLASSES,
                "min": "1",
                "max": "100",
            }),
            "imagen_predeterminada": forms.Select(
                choices=[
                    ("salad", "Ensalada / Verde"),
                    ("soup", "Sopa / Crema"),
                    ("chicken", "Carnes / Pollo / Pescado"),
                    ("dessert", "Postres / Dulces"),
                    ("beverage", "Bebidas / Batidos"),
                    ("breakfast", "Desayuno / Avena / Huevo"),
                    ("snack", "Snack / Frutos secos"),
                ],
                attrs={"class": SELECT_CLASSES}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre de la receta es obligatorio.")
        
        if self.user:
            paciente = getattr(self.instance, "paciente", None)
            qs = Receta.objects.filter(nombre__iexact=nombre, creado_por=self.user, paciente=paciente)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                if paciente:
                    raise ValidationError(f"Ya tienes una receta registrada con el nombre «{nombre}» para este paciente.")
                else:
                    raise ValidationError(f"Ya tienes una plantilla de receta registrada con el nombre «{nombre}».")
        return nombre


class IngredienteRecetaForm(forms.ModelForm):
    """Formulario individual para un ingrediente dentro de una receta."""

    class Meta:
        model = IngredienteReceta
        fields = ["alimento", "cantidad", "nota"]
        widgets = {
            "alimento": forms.Select(attrs={"class": SELECT_CLASSES}),
            "cantidad": forms.NumberInput(attrs={
                "class": INPUT_CLASSES,
                "step": "0.1",
                "min": "0.1",
                "placeholder": "Cantidad en gramos (g)",
            }),
            "nota": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Ej: 1 taza, picada en cubos",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["alimento"].queryset = Alimento.objects.filter(estado=True).order_by("nombre")


class BaseIngredienteRecetaFormSet(forms.BaseInlineFormSet):
    """Formset personalizado para validar los ingredientes de una receta."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        ingredientes_validos = 0
        alimentos_seleccionados = set()

        for form in self.forms:
            if self._should_delete_form(form):
                continue
            
            alimento = form.cleaned_data.get("alimento")
            cantidad = form.cleaned_data.get("cantidad")

            if alimento:
                if alimento in alimentos_seleccionados:
                    form.add_error("alimento", f"El alimento «{alimento.nombre}» ya está en la lista.")
                alimentos_seleccionados.add(alimento)
                
                if not cantidad or cantidad <= 0:
                    form.add_error("cantidad", "La cantidad debe ser mayor a 0.")
                
                ingredientes_validos += 1

        if ingredientes_validos < 1:
            raise ValidationError("Debes agregar al menos un ingrediente válido a la receta.")


IngredienteRecetaFormSet = inlineformset_factory(
    Receta,
    IngredienteReceta,
    form=IngredienteRecetaForm,
    formset=BaseIngredienteRecetaFormSet,
    extra=0,
    can_delete=True,
)
