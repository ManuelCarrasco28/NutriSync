from django.db import models
from django.core.validators import MinValueValidator
from pacientes.models import Paciente
from config.choices import DiaSemana, TipoComida, Objetivo
from .alimentos import Alimento

class PlanNutricional(models.Model):
    """
    Plan de alimentación asignado a un paciente por el nutricionista.
    Un paciente puede tener múltiples planes (histórico) pero solo uno activo.
    La regla 'un solo plan activo' se valida en el formulario y en la vista.
    """
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="planes",
        verbose_name="Paciente",
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del plan",
        help_text="Ej: Plan de pérdida de peso - Enero 2025",
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de fin",
        help_text="Dejar en blanco si el plan no tiene fecha de término definida",
    )
    objetivo = models.CharField(
        max_length=30,
        choices=Objetivo.CHOICES,
        verbose_name="Objetivo",
    )

    # -------------Macros objetivo diario-------------
    calorias_diarias = models.PositiveIntegerField(
        default=2000,
        verbose_name="Calorías diarias (kcal)",
        validators=[MinValueValidator(500)],
    )
    proteinas_g = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Proteínas diarias (g)",
    )
    carbohidratos_g = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Carbohidratos diarios (g)",
    )
    grasas_g = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Grasas diarias (g)",
    )

    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    estado = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Solo puede haber un plan activo por paciente",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Plan Nutricional"
        verbose_name_plural = "Planes Nutricionales"
        indexes = [
            models.Index(fields=["paciente", "estado"]),
            models.Index(fields=["fecha_inicio"]),
        ]

    def __str__(self):
        return f"{self.nombre} — {self.paciente.nombre_completo}"

    @property
    def duracion_dias(self):
        """Calcula la duración del plan en días si tiene fecha de fin definida."""
        if self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days
        return None

    @property
    def objetivo_display(self):
        """Devuelve el label del objetivo para uso en templates."""
        return dict(Objetivo.CHOICES).get(self.objetivo, self.objetivo)


class ComidaPlan(models.Model):
    """
    Una comida específica dentro de un plan nutricional (ej: 'Lunes - Desayuno').
    Tiene ManyToMany con Alimento para sugerir alimentos concretos.
    Se agrupa por día_semana al mostrar el plan organizado lunes→domingo.
    """
    plan = models.ForeignKey(
        PlanNutricional,
        on_delete=models.CASCADE,
        related_name="comidas",
        verbose_name="Plan nutricional",
    )
    dia_semana = models.CharField(
        max_length=10,
        choices=DiaSemana.CHOICES,
        verbose_name="Día de la semana",
        db_index=True,
    )
    tipo_comida = models.CharField(
        max_length=10,
        choices=TipoComida.CHOICES,
        verbose_name="Tipo de comida",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción libre de la comida para el paciente",
    )
    alimentos_sugeridos = models.ManyToManyField(
        Alimento,
        blank=True,
        related_name="comidas_plan",
        verbose_name="Alimentos sugeridos",
    )
    recetas_sugeridas = models.ManyToManyField(
        "Receta",
        blank=True,
        related_name="comidas_plan",
        verbose_name="Recetas sugeridas",
    )
    calorias_estimadas = models.PositiveIntegerField(
        default=0,
        verbose_name="Calorías estimadas (kcal)",
    )

    class Meta:
        ordering = ["dia_semana", "tipo_comida"]
        verbose_name = "Comida del plan"
        verbose_name_plural = "Comidas del plan"
        unique_together = [["plan", "dia_semana", "tipo_comida"]]

    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.get_tipo_comida_display()} ({self.plan.nombre})"
