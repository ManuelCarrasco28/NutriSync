from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from datetime import date, timedelta
from decimal import Decimal


def calcular_evolucion_paciente(paciente, fecha_inicio=None, fecha_fin=None):
    from seguimiento.models import MedidaCorporal
    
    queryset = MedidaCorporal.objects.filter(paciente=paciente)
    if fecha_inicio:
        queryset = queryset.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__lte=fecha_fin)
    
    medidas = queryset.order_by('fecha')
    
    data = {
        'fechas': [],
        'peso': [],
        'imc': [],
        'grasa_corporal': [],
        'masa_muscular': [],
        'cintura': [],
    }
    
    for m in medidas:
        data['fechas'].append(m.fecha.strftime('%d/%m/%Y'))
        data['peso'].append(float(m.peso_kg) if m.peso_kg else None)
        data['imc'].append(float(m.imc) if m.imc else None)
        data['grasa_corporal'].append(float(m.grasa_corporal_pct) if m.grasa_corporal_pct else None)
        data['masa_muscular'].append(float(m.masa_muscular_kg) if m.masa_muscular_kg else None)
        data['cintura'].append(float(m.cintura_cm) if m.cintura_cm else None)
    
    return data


def calcular_distribucion_imc(nutricionista, paciente=None):
    from pacientes.models import Paciente
    from seguimiento.models import MedidaCorporal
    
    if paciente:
        pacientes = Paciente.objects.filter(id=paciente.id, estado=True)
    else:
        pacientes = Paciente.objects.filter(nutricionista=nutricionista, estado=True)
    
    distribucion = {
        'Bajo peso': 0,
        'Normal': 0,
        'Sobrepeso': 0,
        'Obesidad I': 0,
        'Obesidad II': 0,
        'Obesidad III': 0,
        'Sin datos': 0,
    }
    
    for p in pacientes:
        ultima_medida = MedidaCorporal.objects.filter(paciente=p).order_by('-fecha').first()
        if ultima_medida and ultima_medida.imc:
            imc = float(ultima_medida.imc)
            if imc < 18.5:
                distribucion['Bajo peso'] += 1
            elif imc < 25:
                distribucion['Normal'] += 1
            elif imc < 30:
                distribucion['Sobrepeso'] += 1
            elif imc < 35:
                distribucion['Obesidad I'] += 1
            elif imc < 40:
                distribucion['Obesidad II'] += 1
            else:
                distribucion['Obesidad III'] += 1
        else:
            distribucion['Sin datos'] += 1
    
    return distribucion


def calcular_cumplimiento_recomendaciones(nutricionista, fecha_inicio=None, fecha_fin=None, paciente=None):
    from seguimiento.models import Recomendacion
    
    queryset = Recomendacion.objects.filter(paciente__nutricionista=nutricionista)
    if paciente:
        queryset = queryset.filter(paciente=paciente)
    if fecha_inicio:
        queryset = queryset.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__lte=fecha_fin)
    
    total = queryset.count()
    cumplidas = queryset.filter(estado_cumplimiento='cumplida').count()
    parciales = queryset.filter(estado_cumplimiento='parcial').count()
    no_cumplidas = queryset.filter(estado_cumplimiento='no_cumplida').count()
    pendientes = queryset.filter(estado_cumplimiento='pendiente').count()
    
    return {
        'total': total,
        'cumplidas': cumplidas,
        'parciales': parciales,
        'no_cumplidas': no_cumplidas,
        'pendientes': pendientes,
        'porcentaje_cumplimiento': round((cumplidas / total * 100), 1) if total > 0 else 0,
    }


def calcular_ocupacion_agenda(nutricionista, fecha_inicio, fecha_fin):
    from agendas.models import Cita
    
    dias_totales = (fecha_fin - fecha_inicio).days + 1
    horas_disponibles = dias_totales * 10  # 10 horas laborables (8-18)
    
    citas = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista),
        fecha_hora__date__range=[fecha_inicio, fecha_fin]
    ).exclude(tipo='bloqueo')
    
    horas_ocupadas = sum(c.duracion_minutos for c in citas) / 60
    ocupacion = round((horas_ocupadas / horas_disponibles * 100), 1) if horas_disponibles > 0 else 0
    
    return {
        'horas_disponibles': round(horas_disponibles, 1),
        'horas_ocupadas': round(horas_ocupadas, 1),
        'ocupacion': ocupacion,
        'total_citas': citas.count(),
    }


def calcular_citas_por_estado(nutricionista, fecha_inicio=None, fecha_fin=None):
    from agendas.models import Cita
    
    queryset = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista)
    ).exclude(tipo='bloqueo')
    
    if fecha_inicio:
        queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
    
    total = queryset.count()
    programadas = queryset.filter(estado='programada').count()
    completadas = queryset.filter(estado='completada').count()
    canceladas = queryset.filter(estado='cancelada').count()
    no_asistio = queryset.filter(estado='no_asistio').count()
    finalizadas = queryset.filter(estado='finalizada').count()
    
    return {
        'total': total,
        'programadas': programadas,
        'completadas': completadas + finalizadas,
        'canceladas': canceladas,
        'no_asistio': no_asistio,
        'tasa_asistencia': round(((completadas + finalizadas) / (total - programadas) * 100), 1) if (total - programadas) > 0 else 0,
    }


def calcular_citas_por_tipo(nutricionista, fecha_inicio=None, fecha_fin=None):
    from agendas.models import Cita
    
    queryset = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista)
    ).exclude(tipo='bloqueo')
    
    if fecha_inicio:
        queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
    
    tipos = {}
    for tipo_value, tipo_label in Cita._meta.get_field('tipo').choices:
        if tipo_value != 'bloqueo':
            count = queryset.filter(tipo=tipo_value).count()
            tipos[tipo_label] = count
    
    return tipos


def calcular_ingresos(nutricionista, fecha_inicio=None, fecha_fin=None):
    from agendas.models import Cita
    
    queryset = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista),
        estado__in=['completada', 'finalizada']
    )
    
    if fecha_inicio:
        queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
    
    total = queryset.aggregate(total=Sum('costo'))['total'] or Decimal('0')
    cantidad = queryset.count()
    promedio = round(total / cantidad, 2) if cantidad > 0 else Decimal('0')
    
    return {
        'total': float(total),
        'cantidad': cantidad,
        'promedio': float(promedio),
    }


def calcular_ingresos_por_tipo(nutricionista, fecha_inicio=None, fecha_fin=None):
    from agendas.models import Cita
    
    queryset = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista),
        estado__in=['completada', 'finalizada']
    )
    
    if fecha_inicio:
        queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
    
    ingresos_por_tipo = {}
    for tipo_value, tipo_label in Cita._meta.get_field('tipo').choices:
        if tipo_value != 'bloqueo':
            total = queryset.filter(tipo=tipo_value).aggregate(total=Sum('costo'))['total'] or Decimal('0')
            ingresos_por_tipo[tipo_label] = float(total)
    
    return ingresos_por_tipo


def calcular_ingresos_mensuales(nutricionista, meses=6):
    from agendas.models import Cita
    
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=meses * 30)
    
    citas = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista),
        estado__in=['completada', 'finalizada'],
        fecha_hora__date__gte=fecha_inicio
    ).annotate(mes=TruncMonth('fecha_hora')).values('mes').annotate(
        total=Sum('costo'),
        cantidad=Count('id')
    ).order_by('mes')
    
    data = {
        'meses': [],
        'totales': [],
        'cantidades': [],
    }
    
    for c in citas:
        data['meses'].append(c['mes'].strftime('%b %Y'))
        data['totales'].append(float(c['total']) if c['total'] else 0)
        data['cantidades'].append(c['cantidad'])
    
    return data


def calcular_proyeccion_ingresos(nutricionista):
    from agendas.models import Cita
    
    citas_futuras = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista),
        estado='programada',
        fecha_hora__date__gte=date.today()
    )
    
    total = citas_futuras.aggregate(total=Sum('costo'))['total'] or Decimal('0')
    cantidad = citas_futuras.count()
    
    return {
        'total': float(total),
        'cantidad': cantidad,
    }


def calcular_pacientes_activos(nutricionista):
    from pacientes.models import Paciente
    
    total = Paciente.objects.filter(nutricionista=nutricionista, estado=True).count()
    inactivos = Paciente.objects.filter(nutricionista=nutricionista, estado=False).count()
    
    return {
        'activos': total,
        'inactivos': inactivos,
    }


def calcular_productividad(nutricionista, fecha_inicio=None, fecha_fin=None):
    from agendas.models import Cita
    
    queryset = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista)
    ).exclude(tipo='bloqueo')
    
    if fecha_inicio:
        queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
    
    total = queryset.count()
    completadas = queryset.filter(estado__in=['completada', 'finalizada']).count()
    canceladas = queryset.filter(estado='cancelada').count()
    no_asistio = queryset.filter(estado='no_asistio').count()
    
    dias = (fecha_fin - fecha_inicio).days + 1 if fecha_inicio and fecha_fin else 30
    promedio_diario = round(completadas / dias, 1) if dias > 0 else 0
    
    return {
        'total': total,
        'completadas': completadas,
        'canceladas': canceladas,
        'no_asistio': no_asistio,
        'promedio_diario': promedio_diario,
    }


def calcular_ingresos_estimados(nutricionista, fecha_inicio=None, fecha_fin=None):
    from agendas.models import Cita
    
    queryset = Cita.objects.filter(
        Q(paciente__nutricionista=nutricionista) | Q(nutricionista=nutricionista),
        estado='programada'
    )
    
    if fecha_inicio:
        queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
        
    total = queryset.aggregate(total=Sum('costo'))['total'] or Decimal('0')
    cantidad = queryset.count()
    promedio = round(total / cantidad, 2) if cantidad > 0 else Decimal('0')
    
    return {
        'total': float(total),
        'cantidad': cantidad,
        'promedio': float(promedio),
    }
