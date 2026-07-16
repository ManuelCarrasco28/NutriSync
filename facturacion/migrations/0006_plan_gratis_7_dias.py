# facturacion/migrations/0006_plan_gratis_7_dias.py
# Migración de datos: crea el plan de Prueba Gratis de 7 días.

from django.db import migrations


def forwards(apps, schema_editor):
    PlanSuscripcion = apps.get_model("facturacion", "PlanSuscripcion")
    PlanSuscripcion.objects.get_or_create(
        nombre="Prueba Gratis",
        defaults={
            "descripcion": "Acceso total a NutriSync gratis por 7 días. Requiere tarjeta de crédito. Cancela en cualquier momento.",
            "precio_mensual": "0.00",
            "precio_anual": "0.00",
            "limite_pacientes": 10,
            "limite_citas_mes": 20,
            "comision_cobros": "3.00",
            "comision_suscripcion": "0.00",
            "activo": True,
        },
    )


def backwards(apps, schema_editor):
    PlanSuscripcion = apps.get_model("facturacion", "PlanSuscripcion")
    PlanSuscripcion.objects.filter(nombre="Prueba Gratis").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("facturacion", "0005_pago_nutricionista"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
