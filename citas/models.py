# citas/models.py
# Modelo Cita — representa la agenda y las consultas de los pacientes.
# Incluye validaciones atómicas de solapamiento y de estado del paciente.

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from config.choices import TipoCita, EstadoCita
from pacientes.models import Paciente


class Cita(models.Model):
    """
    Representa una consulta médica agendada entre el nutricionista y el paciente.
    La validación en clean() impide el solapamiento de citas y asegura que el paciente esté activo.
    """

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="citas",
        verbose_name="Paciente",
    )
    fecha_hora = models.DateTimeField(
        verbose_name="Fecha y hora",
        help_text="Fecha y hora de inicio de la cita",
    )
    duracion_minutos = models.PositiveIntegerField(
        default=45,
        verbose_name="Duración (minutos)",
        help_text="Duración estimada de la consulta en minutos",
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoCita.CHOICES,
        default=TipoCita.SEGUIMIENTO,
        verbose_name="Tipo de consulta",
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoCita.CHOICES,
        default=EstadoCita.PROGRAMADA,
        verbose_name="Estado",
    )
    motivo = models.TextField(
        blank=True,
        verbose_name="Motivo de la consulta",
        help_text="Breve descripción del motivo de la cita",
    )
    notas_consulta = models.TextField(
        blank=True,
        verbose_name="Notas clínicas",
        help_text="Observaciones, diagnóstico o notas redactadas durante la consulta",
    )
    costo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo de la consulta",
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    class Meta:
        ordering = ["fecha_hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        # Índices para búsquedas y ordenamientos frecuentes
        indexes = [
            models.Index(fields=["fecha_hora", "estado"]),
        ]

    def __str__(self):
        return f"Cita con {self.paciente} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    # ─── Properties de Estado ────────────────────────────────────────────────
    @property
    def esta_programada(self):
        return self.estado == EstadoCita.PROGRAMADA

    @property
    def esta_completada(self):
        return self.estado == EstadoCita.COMPLETADA

    @property
    def esta_cancelada(self):
        return self.estado == EstadoCita.CANCELADA

    @property
    def no_asistio(self):
        return self.estado == EstadoCita.NO_ASISTIO

    @property
    def fecha_fin(self):
        """Devuelve la fecha y hora estimada de finalización de la cita."""
        if self.fecha_hora:
            return self.fecha_hora + timedelta(minutes=self.duracion_minutos)
        return None

    # ─── Validaciones de Negocio ─────────────────────────────────────────────
    def clean(self):
        super().clean()
        errors = {}

        # 1. Validar que el paciente esté activo
        if self.paciente_id:
            # Recargamos de la BD para asegurar que no se use caché obsoleto
            paciente = Paciente.objects.only("estado", "nombre", "apellido").get(pk=self.paciente_id)
            if not paciente.esta_activo:
                errors["paciente"] = ValidationError(
                    "No se pueden programar citas para un paciente inactivo."
                )

        # 2. Validar que la fecha no sea en el pasado (tanto para citas nuevas como para modificaciones de fecha)
        if self.fecha_hora:
            validar_fecha_pasada = False
            if not self.pk:
                # Cita nueva: la fecha siempre debe ser a futuro
                validar_fecha_pasada = True
            else:
                # Edición: solo validamos si la fecha ha sido modificada
                try:
                    original = self.__class__.objects.get(pk=self.pk)
                    if self.fecha_hora != original.fecha_hora:
                        validar_fecha_pasada = True
                except self.__class__.DoesNotExist:
                    validar_fecha_pasada = True

            if validar_fecha_pasada:
                # Añadimos un pequeño margen de 1 minuto para evitar errores por desfases de milisegundos
                if self.fecha_hora < timezone.now() - timedelta(minutes=1):
                    errors["fecha_hora"] = ValidationError(
                        "La fecha y hora de la cita no puede ser en el pasado."
                    )

        # 3. Validar solapamiento de horarios para el mismo nutricionista
        if self.paciente_id and self.fecha_hora and self.duracion_minutos:
            nutricionista = self.paciente.nutricionista
            inicio_nuevo = self.fecha_hora
            fin_nuevo = self.fecha_fin
            fecha_dia = self.fecha_hora.date()

            # Obtenemos todas las citas activas de este nutricionista en el mismo día
            citas_dia = Cita.objects.filter(
                paciente__nutricionista=nutricionista,
                fecha_hora__date=fecha_dia,
            ).exclude(estado=EstadoCita.CANCELADA).select_related("paciente")

            # Excluimos la cita actual en caso de edición
            if self.pk:
                citas_dia = citas_dia.exclude(pk=self.pk)

            for cita_existente in citas_dia:
                inicio_existente = cita_existente.fecha_hora
                fin_existente = cita_existente.fecha_fin

                # Condición de traslape: (inicio1 < fin2) AND (fin1 > inicio2)
                if inicio_existente < fin_nuevo and fin_existente > inicio_nuevo:
                    errors["fecha_hora"] = ValidationError(
                        f"El horario seleccionado se solapa con otra cita programada para el paciente "
                        f"{cita_existente.paciente.nombre_completo} "
                        f"({inicio_existente.strftime('%H:%M')} - {fin_existente.strftime('%H:%M')})."
                    )
                    break

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Siguiendo los estándares del docente de la sesión 2,
        # forzamos full_clean() antes de guardar para asegurar la integridad de datos
        self.full_clean()
        super().save(*args, **kwargs)

