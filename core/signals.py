# core/signals.py
# Crea PerfilNutricionista automáticamente al crear un User (excepto staff).

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilNutricionista


@receiver(post_save, sender=User)
def crear_perfil_nutricionista(sender, instance, created, **kwargs):
    """Crea perfil para usuarios nuevos que no sean staff."""
    if created and not instance.is_staff:
        nombre = f"{instance.first_name} {instance.last_name}".strip()
        PerfilNutricionista.objects.get_or_create(
            usuario=instance,
            defaults={"nombre_completo": nombre or instance.username},
        )
