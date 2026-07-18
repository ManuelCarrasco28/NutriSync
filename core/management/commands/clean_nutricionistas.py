from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from facturacion.models import Pago
from facturacion.choices import MetodoPago, EstadoPago
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Limpia las cuentas de nutricionistas locales u online sin metodo de pago y rellena una tarjeta para manuel.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando limpieza de nutricionistas sin metodo de pago...")
        
        # 1. Obtener todos los usuarios con perfil de nutricionista
        nutricionistas = User.objects.filter(perfil__rol='nutricionista')
        
        deleted_count = 0
        manuel_filled = False
        
        for user in nutricionistas:
            # Verificar si tiene algun pago de suscripcion completado con metodo de pago valido
            pagos_validos = user.pagos_facturacion.filter(
                estado='completado'
            )
            
            tiene_metodo = False
            for pago in pagos_validos:
                notas = pago.notas or ""
                if "Tarjeta terminada en" in notas or "Celular Yape:" in notas or "PayPal Email:" in notas:
                    if "removido" not in notas:
                        tiene_metodo = True
                        break
            
            if not tiene_metodo:
                if user.username == 'manuel':
                    # No eliminar, en su lugar rellenarle una tarjeta
                    suscripcion = getattr(user, 'suscripcion', None)
                    monto = Decimal("0.00")
                    plan_nombre = "Prueba Gratis"
                    tipo_fac = "mensual"
                    
                    if suscripcion:
                        monto = suscripcion.precio_aplicado
                        plan_nombre = suscripcion.plan.nombre
                        tipo_fac = suscripcion.tipo_facturacion
                    
                    notas_card = f"Cobro inicial plan {plan_nombre} ({tipo_fac}) - Tarjeta terminada en 4321"
                    
                    # Crear pago simulado
                    Pago.objects.create(
                        nutricionista=user,
                        monto=monto,
                        metodo_pago=MetodoPago.STRIPE,
                        referencia=f"CULQI-MANUEL-{user.pk}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                        estado=EstadoPago.COMPLETADO,
                        comision_stripe=Decimal("0.00"),
                        monto_neto=monto,
                        notas=notas_card,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"-> Cuenta de 'manuel' conservada. Se le genero un metodo de pago simulado (tarjeta terminada en 4321)."
                    ))
                    manuel_filled = True
                else:
                    # Eliminar nutricionista
                    username = user.username
                    email = user.email
                    user.delete()
                    self.stdout.write(self.style.WARNING(
                        f"-> Eliminado usuario nutricionista sin metodo de pago: {username} ({email})"
                    ))
                    deleted_count += 1
            else:
                if user.username == 'manuel':
                    self.stdout.write(
                        f"-> El usuario 'manuel' ya tiene un metodo de pago guardado."
                    )
                    manuel_filled = True
                else:
                    self.stdout.write(
                        f"-> Cuenta conservada (tiene metodo de pago): {user.username}"
                    )
                    
        self.stdout.write(self.style.SUCCESS(
            f"\nLimpieza completada. Cuentas eliminadas: {deleted_count}. Rellenado a manuel: {'Si' if manuel_filled else 'No'}."
        ))
