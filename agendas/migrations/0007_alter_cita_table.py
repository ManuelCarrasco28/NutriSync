# Esta migración es un no-op: la tabla ya existía como citas_cita en la BD
# gracias a db_table = "citas_cita" en el Meta del modelo original.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agendas', '0006_alter_cita_estado'),
    ]

    operations = [
        # La tabla en PostgreSQL ya se llama citas_cita.
        # No se necesita renombrarla.
    ]
