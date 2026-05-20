# core/views.py
# Vistas de autenticación, dashboard y perfil del nutricionista.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from config.choices import EstadoNutricionista
from .forms import PerfilNutricionistaForm
from citas.models import Cita
from pacientes.models import Paciente


def login_view(request):
    """
    Vista de login con validación adicional de estado del perfil.
    Un nutricionista deshabilitado no puede iniciar sesión aunque su contraseña sea correcta.
    """
    # Si ya está autenticado, redirige al dashboard directamente
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Validamos que el perfil esté habilitado antes de permitir el acceso
            try:
                perfil = user.perfil
                if perfil.estado != EstadoNutricionista.HABILITADO:
                    messages.error(
                        request,
                        "Tu cuenta está deshabilitada. Contacta al administrador.",
                    )
                    return render(request, "core/login.html")
            except Exception:
                # Si no tiene perfil (edge case), se crea implícitamente por el signal
                pass

            login(request, user)
            messages.success(request, f"Bienvenido, {user.first_name or user.username}.")
            # Respeta el parámetro 'next' para redirigir a la página que intentaba acceder
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "core/login.html")


@login_required
def logout_view(request):
    """Cierra la sesión y redirige al login."""
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("core:login")


@login_required
def dashboard_view(request):
    """
    Dashboard principal con métricas reales de pacientes y citas.
    Muestra el total de pacientes activos, las citas de hoy y las próximas consultas de la agenda.
    """
    hoy = timezone.localtime(timezone.now())
    fecha_hoy = hoy.date()
    inicio_hoy = hoy.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Total pacientes activos
    pacientes_activos_count = Paciente.objects.filter(
        nutricionista=request.user, 
        estado=True
    ).count()

    # 2. Citas programadas para hoy (excluyendo canceladas)
    citas_hoy_count = Cita.objects.filter(
        paciente__nutricionista=request.user,
        fecha_hora__date=fecha_hoy
    ).exclude(estado='cancelada').count()

    # 3. Próximas 5 citas a partir del inicio del día de hoy
    proximas_citas = Cita.objects.filter(
        paciente__nutricionista=request.user,
        fecha_hora__gte=inicio_hoy
    ).exclude(
        estado='cancelada'
    ).select_related('paciente').order_by('fecha_hora')[:5]

    context = {
        "pacientes_activos_count": pacientes_activos_count,
        "citas_hoy_count": citas_hoy_count,
        "proximas_citas": proximas_citas,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def perfil_view(request):
    """
    Ver y editar el perfil profesional del nutricionista autenticado.
    get_or_create garantiza que siempre haya un perfil disponible (no falla si falta).
    """
    perfil, _ = request.user.perfil.__class__.objects.get_or_create(
        usuario=request.user,
        defaults={"nombre_completo": request.user.username},
    )

    if request.method == "POST":
        form = PerfilNutricionistaForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("core:perfil")
    else:
        form = PerfilNutricionistaForm(instance=perfil)

    return render(request, "core/perfil.html", {"form": form})


# ─── Handlers de error personalizados ────────────────────────────────────────

def error_404(request, exception):
    """Página 404 personalizada con diseño consistente al sistema."""
    return render(request, "404.html", status=404)


def error_500(request):
    """Página 500 personalizada con diseño consistente al sistema."""
    return render(request, "500.html", status=500)
