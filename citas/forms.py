# citas/forms.py
# Formulario de registro y edición de Citas.
# Filtra dinámicamente los pacientes del nutricionista autenticado y aplica el sistema de diseño.

from django import forms
from django.utils import timezone
from .models import Cita
from pacientes.models import Paciente


class CitaForm(forms.ModelForm):
    """
    Formulario para crear y actualizar Citas.
    Filtra los pacientes para mostrar únicamente los del nutricionista logueado y que estén activos.
    """

    class Meta:
        model = Cita
        fields = [
            "paciente",
            "fecha_hora",
            "duracion_minutos",
            "tipo",
            "estado",
            "motivo",
            "notas_consulta",
            "costo",
        ]
        widgets = {
            "fecha_hora": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "placeholder": "Selecciona fecha y hora",
                }
            ),
            "motivo": forms.Textarea(attrs={"rows": 2, "placeholder": "Motivo de la consulta"}),
            "notas_consulta": forms.Textarea(attrs={"rows": 4, "placeholder": "Notas clínicas de la evolución"}),
            "duracion_minutos": forms.NumberInput(attrs={"min": 10, "max": 180, "step": 5}),
            "costo": forms.NumberInput(attrs={"min": 0, "step": "0.01", "placeholder": "0.00"}),
        }

    def __init__(self, *args, **kwargs):
        # Extraemos el usuario (nutricionista) de los kwargs pasados por la vista
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # 1. Filtrado dinámico de pacientes: solo los del nutricionista logueado y activos
        if self.user:
            # Mostramos únicamente los pacientes que pertenecen a este profesional y que estén activos (estado=True)
            self.fields["paciente"].queryset = Paciente.objects.filter(
                nutricionista=self.user,
                estado=True,
            ).order_by("nombre", "apellido")
        else:
            # Fallback seguro en caso de que no se pase usuario
            self.fields["paciente"].queryset = Paciente.objects.none()

        # 2. Restringir selección de fechas pasadas en el navegador para citas nuevas
        if not self.instance.pk:
            ahora_local = timezone.localtime(timezone.now())
            # Formato requerido por el input HTML5 datetime-local: YYYY-MM-DDTHH:MM
            self.fields["fecha_hora"].widget.attrs["min"] = ahora_local.strftime("%Y-%m-%dT%H:%M")

        # 3. Aplicar clases CSS del sistema de diseño (Tailwind) a todos los campos
        for field_name, field in self.fields.items():
            if field_name == "fecha_hora":
                # Dejamos espacio para el icono a la izquierda (pl-10)
                base_classes = (
                    "mt-1 block w-full rounded-lg border border-slate-200 pl-10 pr-3 py-2 text-slate-800 "
                    "placeholder-slate-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 "
                    "transition duration-150"
                )
            else:
                base_classes = (
                    "mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-slate-800 "
                    "placeholder-slate-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 "
                    "transition duration-150"
                )

            # Si es un checkbox (no lo hay en este form por defecto, pero por robustez)
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "rounded text-teal-600 focus:ring-teal-500 border-slate-300"
            else:
                existing_classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{base_classes} {existing_classes}".strip()
