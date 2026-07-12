from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from config.choices import DiaSemana, TipoComida, Objetivo
from .alimentos import Alimento

class PlanNutricional(models.Model):
    """
    Modelo/Plantilla de plan nutricional creado por un nutricionista.
    No pertenece a ningún paciente y sirve como biblioteca reusable.
    """
    ESTADOS = [
        ('Borrador', 'Borrador'),
        ('Activo', 'Activo'),
        ('Archivado', 'Archivado'),
    ]

    nutricionista = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="modelos_planes",
        verbose_name="Nutricionista",
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del plan",
        help_text="Ej: Plan hiperproteico de definición",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Breve descripción del propósito de este modelo de plan"
    )
    objetivo = models.CharField(
        max_length=30,
        choices=Objetivo.CHOICES,
        verbose_name="Objetivo",
    )
    tipo_paciente = models.CharField(
        max_length=100,
        default="General",
        verbose_name="Tipo de paciente",
        help_text="Ej: Adulto activo, Deportista, Sedentario"
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
    fibra_g = models.PositiveIntegerField(
        default=25,
        verbose_name="Fibra (g)"
    )
    agua_recomendada = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=2.5,
        verbose_name="Agua recomendada (L)"
    )
    num_comidas = models.PositiveIntegerField(
        default=4,
        verbose_name="Número de comidas"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='Borrador',
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Modelo de Plan"
        verbose_name_plural = "Modelos de Planes"
        indexes = [
            models.Index(fields=["nutricionista", "estado"]),
        ]

    def __str__(self):
        return f"{self.nombre} — {self.objetivo_display}"

    @property
    def objetivo_display(self):
        """Devuelve el label del objetivo para uso en templates."""
        return dict(Objetivo.CHOICES).get(self.objetivo, self.objetivo)


class ComidaPlan(models.Model):
    """
    Una comida específica dentro de un modelo de plan (ej: Desayuno, Almuerzo).
    Se vincula a una Receta existente en el sistema.
    """
    plan = models.ForeignKey(
        PlanNutricional,
        on_delete=models.CASCADE,
        related_name="comidas",
        verbose_name="Plan nutricional",
    )
    tipo_comida = models.CharField(
        max_length=50,
        verbose_name="Nombre de la comida",
        help_text="Ej: Desayuno, Merienda, Cena"
    )
    hora_sugerida = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horario sugerido"
    )
    receta = models.ForeignKey(
        "Receta",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comidas_plan",
        verbose_name="Receta seleccionada"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones sugeridas"
    )

    class Meta:
        ordering = ["hora_sugerida", "id"]
        verbose_name = "Comida del plan"
        verbose_name_plural = "Comidas del plan"

    def __str__(self):
        return f"{self.tipo_comida} - {self.receta.nombre} ({self.plan.nombre})"
