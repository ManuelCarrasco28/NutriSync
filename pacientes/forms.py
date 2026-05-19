# pacientes/forms.py
# Formulario para crear y editar pacientes con validaciones de negocio.
# Usa widgets Tailwind para mantener la consistencia visual del sistema.

from django import forms
from .models import Paciente


class PacienteForm(forms.ModelForm):
    """Formulario para crear/editar la ficha de un paciente."""

    class Meta:
        model = Paciente
        # Excluimos nutricionista (se asigna en la vista) y fechas automáticas
        fields = [
            "nombre",
            "apellido",
            "fecha_nacimiento",
            "sexo",
            "ocupacion",
            "telefono",
            "email",
            "direccion",
            "condiciones_medicas",
            "alergias",
            "notas_generales",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "placeholder": "Nombre del paciente",
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "placeholder": "Apellido del paciente",
                }
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                },
                format="%Y-%m-%d",
            ),
            "sexo": forms.Select(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800 bg-white",
                }
            ),
            "ocupacion": forms.TextInput(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "placeholder": "Ej: Ingeniero, Estudiante, Ama de casa",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "placeholder": "Ej: +51 999 000 000",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "placeholder": "correo@ejemplo.com",
                }
            ),
            "direccion": forms.Textarea(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "rows": 2,
                    "placeholder": "Dirección del domicilio",
                }
            ),
            "condiciones_medicas": forms.Textarea(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "rows": 3,
                    "placeholder": "Condiciones médicas relevantes del paciente",
                }
            ),
            "alergias": forms.Textarea(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "rows": 3,
                    "placeholder": "Alergias conocidas (alimentos, medicamentos, etc.)",
                }
            ),
            "notas_generales": forms.Textarea(
                attrs={
                    "class": "w-full border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-800",
                    "rows": 3,
                    "placeholder": "Observaciones generales relevantes para el nutricionista",
                }
            ),
        }

    def clean_nombre(self):
        """Normaliza el nombre: primera letra mayúscula, sin espacios extra."""
        nombre = self.cleaned_data.get("nombre", "")
        return nombre.strip().title()

    def clean_apellido(self):
        """Normaliza el apellido: primera letra mayúscula, sin espacios extra."""
        apellido = self.cleaned_data.get("apellido", "")
        return apellido.strip().title()

    def clean_telefono(self):
        """Valida que el teléfono contenga solo dígitos, espacios y guiones básicos."""
        telefono = self.cleaned_data.get("telefono", "")
        if telefono:
            # Permite números, espacios, +, -, paréntesis
            import re

            if not re.match(r"^[+\d\s\-()]+$", telefono):
                raise forms.ValidationError(
                    "El teléfono solo puede contener números, espacios, +, - y paréntesis."
                )
        return telefono

    def clean_fecha_nacimiento(self):
        """Valida que la fecha sea razonable: año >= 1900 y no futura."""
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha:
            from datetime import date

            today = date.today()
            # No puede ser una fecha futura
            if fecha > today:
                raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
            # El año debe ser razonable (evita valores como 200900)
            if fecha.year < 1900:
                raise forms.ValidationError("El año debe ser posterior a 1900.")
            # Edad máxima razonable: 120 años
            if fecha.year < today.year - 120:
                raise forms.ValidationError("La fecha de nacimiento no es válida.")
        return fecha
