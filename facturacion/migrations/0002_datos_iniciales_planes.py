# facturacion/migrations/0002_datos_iniciales_planes.py
# Migración de datos: crea los planes de suscripción predeterminados.

from django.db import migrations


PLANES = [
    {
        "nombre": "Básico",
        "descripcion": "Ideal para nutricionistas que recién comienzan. Incluye las funcionalidades esenciales del sistema.",
        "precio_mensual": "99.00",
        "precio_anual": "990.00",
        "limite_pacientes": 30,
        "limite_citas_mes": 60,
        "comision_cobros": "3.00",
        "comision_suscripcion": "0.00",
        "activo": True,
    },
    {
        "nombre": "Profesional",
        "descripcion": "Para nutricionistas con clientela establecida. Mayor capacidad y comisiones reducidas.",
        "precio_mensual": "199.00",
        "precio_anual": "1990.00",
        "limite_pacientes": 100,
        "limite_citas_mes": 200,
        "comision_cobros": "2.00",
        "comision_suscripcion": "0.00",
        "activo": True,
    },
]


def forwards(apps, schema_editor):
    PlanSuscripcion = apps.get_model("facturacion", "PlanSuscripcion")
    for plan_data in PLANES:
        PlanSuscripcion.objects.get_or_create(
            nombre=plan_data["nombre"],
            defaults=plan_data,
        )


def backwards(apps, schema_editor):
    PlanSuscripcion = apps.get_model("facturacion", "PlanSuscripcion")
    PlanSuscripcion.objects.filter(
        nombre__in=[p["nombre"] for p in PLANES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("facturacion", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
