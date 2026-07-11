from django.db import migrations


def move_data(apps, schema_editor):
    NotaClinica = apps.get_model('seguimiento', 'NotaClinica')
    for nota in NotaClinica.objects.all():
        if nota.contenido:
            nota.observaciones_clinicas = nota.contenido
            nota.save()

class Migration(migrations.Migration):

    dependencies = [
        ('seguimiento', '0003_notaclinica_motivo_consulta_and_more'),
    ]

    operations = [
        migrations.RunPython(move_data),
    ]

