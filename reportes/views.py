from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, timedelta
from pacientes.models import Paciente
from agendas.models import Cita
from seguimiento.models import MedidaCorporal, Recomendacion
from . import utils
import json
import calendar


@login_required
def dashboard_reportes(request):
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    fin_mes = hoy.replace(day=calendar.monthrange(hoy.year, hoy.month)[1])
    
    pacientes_activos = Paciente.objects.filter(nutricionista=request.user, estado=True).count()
    
    citas_mes = Cita.objects.filter(
        paciente__nutricionista=request.user,
        fecha_hora__date__range=[inicio_mes, fin_mes]
    ).count()
    
    ingresos_mes = utils.calcular_ingresos(request.user, inicio_mes, fin_mes)
    ingresos_estimados_mes = utils.calcular_ingresos_estimados(request.user, inicio_mes, fin_mes)
    
    cumplimiento = utils.calcular_cumplimiento_recomendaciones(request.user, inicio_mes, fin_mes)
    
    context = {
        'pacientes_activos': pacientes_activos,
        'citas_mes': citas_mes,
        'ingresos_mes': ingresos_mes['total'],
        'ingresos_estimados_mes': ingresos_estimados_mes['total'],
        'cumplimiento': cumplimiento['porcentaje_cumplimiento'],
    }
    
    return render(request, 'reportes/dashboard.html', context)


@login_required
def reportes_clinicos(request):
    paciente_id = request.GET.get('paciente')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    fecha_inicio = None
    fecha_fin = None
    
    if fecha_inicio_str:
        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
        except ValueError:
            fecha_inicio = date.today() - timedelta(days=90)
    else:
        fecha_inicio = date.today() - timedelta(days=90)
    
    if fecha_fin_str:
        try:
            fecha_fin = date.fromisoformat(fecha_fin_str)
        except ValueError:
            fecha_fin = date.today()
    else:
        fecha_fin = date.today()
    
    pacientes = Paciente.objects.filter(nutricionista=request.user, estado=True).order_by('nombre', 'apellido')
    
    paciente_seleccionado = None
    if paciente_id:
        try:
            paciente_seleccionado = Paciente.objects.get(id=paciente_id, nutricionista=request.user)
        except Paciente.DoesNotExist:
            pass
    
    evolucion = {}
    if paciente_seleccionado:
        evolucion = utils.calcular_evolucion_paciente(paciente_seleccionado, fecha_inicio, fecha_fin)
    
    distribucion_imc = utils.calcular_distribucion_imc(request.user, paciente_seleccionado)
    cumplimiento = utils.calcular_cumplimiento_recomendaciones(request.user, fecha_inicio, fecha_fin, paciente_seleccionado)
    
    context = {
        'pacientes': pacientes,
        'paciente_seleccionado': paciente_seleccionado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'evolucion': json.dumps(evolucion) if evolucion else '{}',
        'distribucion_imc_labels': json.dumps(list(distribucion_imc.keys())),
        'distribucion_imc_values': json.dumps(list(distribucion_imc.values())),
        'cumplimiento': cumplimiento,
    }
    
    return render(request, 'reportes/clinicos.html', context)


@login_required
def reportes_operativos(request):
    vista = request.GET.get('vista', 'mes')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    hoy = date.today()
    
    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
            fecha_fin = date.fromisoformat(fecha_fin_str)
        except ValueError:
            if vista == 'semana':
                fecha_inicio = hoy - timedelta(days=7)
                fecha_fin = hoy
            elif vista == 'mes':
                fecha_inicio = hoy - timedelta(days=30)
                fecha_fin = hoy
            else:
                fecha_inicio = hoy - timedelta(days=365)
                fecha_fin = hoy
    else:
        if vista == 'semana':
            fecha_inicio = hoy - timedelta(days=7)
            fecha_fin = hoy
        elif vista == 'mes':
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy
        else:
            fecha_inicio = hoy - timedelta(days=365)
            fecha_fin = hoy
    
    ocupacion = utils.calcular_ocupacion_agenda(request.user, fecha_inicio, fecha_fin)
    citas_estado = utils.calcular_citas_por_estado(request.user, fecha_inicio, fecha_fin)
    citas_tipo = utils.calcular_citas_por_tipo(request.user, fecha_inicio, fecha_fin)
    pacientes_info = utils.calcular_pacientes_activos(request.user)
    productividad = utils.calcular_productividad(request.user, fecha_inicio, fecha_fin)
    
    context = {
        'vista': vista,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ocupacion': ocupacion,
        'citas_estado': citas_estado,
        'citas_tipo_labels': json.dumps(list(citas_tipo.keys())),
        'citas_tipo_values': json.dumps(list(citas_tipo.values())),
        'pacientes_info': pacientes_info,
        'productividad': productividad,
    }
    
    return render(request, 'reportes/operativos.html', context)


@login_required
def reportes_financieros(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    hoy = date.today()
    
    if fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
            fecha_fin = date.fromisoformat(fecha_fin_str)
        except ValueError:
            fecha_inicio = hoy - timedelta(days=30)
            fecha_fin = hoy
    else:
        fecha_inicio = hoy - timedelta(days=30)
        fecha_fin = hoy
    
    ingresos = utils.calcular_ingresos(request.user, fecha_inicio, fecha_fin)
    ingresos_estimados = utils.calcular_ingresos_estimados(request.user, fecha_inicio, fecha_fin)
    ingresos_tipo = utils.calcular_ingresos_por_tipo(request.user, fecha_inicio, fecha_fin)
    ingresos_mensuales = utils.calcular_ingresos_mensuales(request.user, meses=6)
    proyeccion = utils.calcular_proyeccion_ingresos(request.user)
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ingresos': ingresos,
        'ingresos_estimados': ingresos_estimados,
        'ingresos_tipo': ingresos_tipo,
        'ingresos_tipo_labels': json.dumps(list(ingresos_tipo.keys())),
        'ingresos_tipo_values': json.dumps(list(ingresos_tipo.values())),
        'ingresos_mensuales_meses': json.dumps(ingresos_mensuales['meses']),
        'ingresos_mensuales_totales': json.dumps(ingresos_mensuales['totales']),
        'proyeccion': proyeccion,
    }
    
    return render(request, 'reportes/financieros.html', context)
