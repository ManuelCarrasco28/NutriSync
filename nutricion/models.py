# nutricion/models.py
# Modelos del módulo de Planes Nutricionales y Base de Alimentos.
# Estructura: Alimento (catálogo) → ComidaPlan (ManyToMany) → PlanNutricional (asignado a paciente).

from django.db import models
from django.core.validators import MinValueValidator
from pacientes.models import Paciente
from config.choices import DiaSemana, TipoComida, Objetivo


# ─── Categorías de alimentos ─────────────────────────────────────────────────

class CategoriaAlimento(models.TextChoices):
    """Categorías para organizar la base de alimentos del catálogo."""
    CEREALES = "cereales", "Cereales y granos"
    LACTEOS = "lacteos", "Lácteos"
    CARNES = "carnes", "Carnes y aves"
    PESCADOS = "pescados", "Pescados y mariscos"
    HUEVOS = "huevos", "Huevos"
    LEGUMBRES = "legumbres", "Legumbres"
    VERDURAS = "verduras", "Verduras y hortalizas"
    FRUTAS = "frutas", "Frutas"
    GRASAS = "grasas", "Grasas y aceites"
    BEBIDAS = "bebidas", "Bebidas"
    SNACKS = "snacks", "Snacks y aperitivos"
    OTROS = "otros", "Otros"


# ─── Alimento ─────────────────────────────────────────────────────────────────

class Alimento(models.Model):
    """
    Base de datos de alimentos con información nutricional por 100g.
    Sirve como catálogo compartido para todos los planes nutricionales.
    El campo 'estado' permite dar de baja un alimento sin borrarlo (soft-delete).
    """

    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del alimento",
        db_index=True,  # Índice para acelerar búsquedas por nombre (operación frecuente)
    )
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaAlimento.choices,
        default=CategoriaAlimento.OTROS,
        verbose_name="Categoría",
        db_index=True,  # Índice para filtrado por categoría en el catálogo
    )

    # ─── Información nutricional por 100g ────────────────────────────────────
    # Valores por 100g como convención estándar nutricional (facilita comparaciones)
    calorias_100g = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Calorías (kcal/100g)",
        default=0,
    )
    proteinas_100g = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Proteínas (g/100g)",
        default=0,
    )
    carbohidratos_100g = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Carbohidratos (g/100g)",
        default=0,
    )
    grasas_100g = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Grasas (g/100g)",
        default=0,
    )
    fibra_100g = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Fibra (g/100g)",
        default=0,
    )

    porcion_referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Porción de referencia",
        help_text="Ej: 1 taza (240ml), 1 unidad mediana (150g)",
    )

    # Soft-delete: baja el alimento del catálogo activo sin eliminarlo
    estado = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Desmarcar para dar de baja el alimento del catálogo",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Alimento"
        verbose_name_plural = "Alimentos"
        indexes = [
            # Búsqueda combinada nombre + categoría: operación más frecuente en el catálogo
            models.Index(fields=["nombre", "categoria"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


# ─── PlanNutricional ──────────────────────────────────────────────────────────

class PlanNutricional(models.Model):
    """
    Plan de alimentación asignado a un paciente por el nutricionista.
    Un paciente puede tener múltiples planes (histórico) pero solo uno activo.
    La regla 'un solo plan activo' se valida en el formulario y en la vista.
    """

    # FK a Paciente (que ya tiene FK a nutricionista): aislamiento de datos en cascada.
    # Al filtrar por paciente__nutricionista=request.user, se garantiza el aislamiento.
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

    # ─── Macros objetivo diario ──────────────────────────────────────────────
    # Se registran como meta diaria para que el nutricionista pueda hacer seguimiento
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

    # Soft-delete: un plan inactivo se conserva en el historial
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
            # Búsqueda de planes activos de un paciente: operación más frecuente
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


# ─── ComidaPlan ──────────────────────────────────────────────────────────────

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
        db_index=True,  # Índice para agrupar comidas por día al mostrar el plan
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
    # ManyToMany con Alimento: sugiere alimentos del catálogo para esta comida.
    # Usamos through=None (tabla implícita) porque no se necesitan campos extra en la relación.
    alimentos_sugeridos = models.ManyToManyField(
        Alimento,
        blank=True,
        related_name="comidas_plan",
        verbose_name="Alimentos sugeridos",
    )
    calorias_estimadas = models.PositiveIntegerField(
        default=0,
        verbose_name="Calorías estimadas (kcal)",
    )

    class Meta:
        ordering = ["dia_semana", "tipo_comida"]
        verbose_name = "Comida del plan"
        verbose_name_plural = "Comidas del plan"
        # Un plan no debería tener la misma comida dos veces el mismo día
        unique_together = [["plan", "dia_semana", "tipo_comida"]]

    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.get_tipo_comida_display()} ({self.plan.nombre})"
