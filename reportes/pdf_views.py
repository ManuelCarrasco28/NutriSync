from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from datetime import date, timedelta
from . import utils


def render_pdf(template_path, context, filename):
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=result, encoding='utf-8')
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Error generando PDF", status=500)


@login_required
def pdf_clinicos(request):
    paciente_id = request.GET.get('paciente')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    secciones = request.GET.get('secciones', 'todas')
    
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
    
    from pacientes.models import Paciente
    
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
        'paciente_seleccionado': paciente_seleccionado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'evolucion': evolucion,
        'distribucion_imc': distribucion_imc,
        'cumplimiento': cumplimiento,
        'nutricionista': request.user,
        'secciones': secciones.split(',') if secciones != 'todas' else ['todas'],
    }
    
    return render_pdf('reportes/pdf/clinico_pdf.html', context, 'reporte_clinico.pdf')


@login_required
def pdf_operativos(request):
    vista = request.GET.get('vista', 'mes')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    secciones = request.GET.get('secciones', 'todas')
    
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
        'citas_tipo': citas_tipo,
        'pacientes_info': pacientes_info,
        'productividad': productividad,
        'nutricionista': request.user,
        'secciones': secciones.split(',') if secciones != 'todas' else ['todas'],
    }
    
    return render_pdf('reportes/pdf/operativo_pdf.html', context, 'reporte_operativo.pdf')


@login_required
def pdf_financieros(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    secciones = request.GET.get('secciones', 'todas')
    
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
        'ingresos_mensuales': ingresos_mensuales,
        'proyeccion': proyeccion,
        'nutricionista': request.user,
        'secciones': secciones.split(',') if secciones != 'todas' else ['todas'],
    }
    
    return render_pdf('reportes/pdf/financiero_pdf.html', context, 'reporte_financiero.pdf')
