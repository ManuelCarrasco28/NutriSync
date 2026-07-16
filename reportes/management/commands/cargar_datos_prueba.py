from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pacientes.models import Paciente, Consulta
from agendas.models import Cita
from seguimiento.models import MedidaCorporal, Recomendacion, NotaClinica
from datetime import date, timedelta, time, datetime
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Carga datos de prueba para reportes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Borra datos existentes antes de crear nuevos',
        )
        parser.add_argument(
            '--pacientes',
            type=int,
            default=18,
            help='Cantidad de pacientes a crear (default: 18)',
        )

    def handle(self, *args, **options):
        limpiar = options['limpiar']
        cantidad_pacientes = options['pacientes']

        self.stdout.write('Iniciando carga de datos de prueba...')

        # 1. Obtener nutricionista (admin)
        try:
            nutricionista = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stderr.write('Error: No existe usuario admin. Crear superusuario primero.')
            return

        # 2. Limpiar datos si se solicita
        if limpiar:
            self.stdout.write('Limpiando datos existentes...')
            Paciente.objects.filter(nutricionista=nutricionista).delete()
            Cita.objects.filter(nutricionista=nutricionista).delete()
            self.stdout.write(self.style.SUCCESS('Datos limpiados'))

        # 3. Crear pacientes
        self.stdout.write(f'Creando {cantidad_pacientes} pacientes...')
        pacientes = self.crear_pacientes(nutricionista, cantidad_pacientes)
        self.stdout.write(self.style.SUCCESS(f'{len(pacientes)} pacientes creados'))

        # 4. Crear citas
        self.stdout.write('Creando citas...')
        citas = self.crear_citas(pacientes, nutricionista, meses=6)
        self.stdout.write(self.style.SUCCESS(f'{len(citas)} citas creadas'))

        # 5. Crear consultas clínicas
        self.stdout.write('Creando consultas clínicas...')
        consultas = self.crear_consultas(pacientes, nutricionista)
        self.stdout.write(self.style.SUCCESS(f'{len(consultas)} consultas creadas'))

        # 6. Crear medidas corporales
        self.stdout.write('Creando medidas corporales...')
        medidas = self.crear_medidas(pacientes, consultas)
        self.stdout.write(self.style.SUCCESS(f'{len(medidas)} medidas creadas'))

        # 7. Crear recomendaciones
        self.stdout.write('Creando recomendaciones...')
        recomendaciones = self.crear_recomendaciones(pacientes, nutricionista, consultas)
        self.stdout.write(self.style.SUCCESS(f'{len(recomendaciones)} recomendaciones creadas'))

        # 8. Crear notas clínicas
        self.stdout.write('Creando notas clínicas...')
        notas = self.crear_notas(pacientes, nutricionista, consultas)
        self.stdout.write(self.style.SUCCESS(f'{len(notas)} notas creadas'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDatos de prueba cargados exitosamente:\n'
            f'  - {len(pacientes)} pacientes\n'
            f'  - {len(citas)} citas\n'
            f'  - {len(consultas)} consultas\n'
            f'  - {len(medidas)} medidas corporales\n'
            f'  - {len(recomendaciones)} recomendaciones\n'
            f'  - {len(notas)} notas clínicas'
        ))

    def crear_pacientes(self, nutricionista, cantidad):
        """Crea pacientes con datos realistas"""
        nombres_m = ['Carlos', 'Juan', 'Miguel', 'Luis', 'José', 'Pedro', 'Andrés', 'Roberto', 'Fernando', 'Diego']
        nombres_f = ['María', 'Ana', 'Laura', 'Carmen', 'Rosa', 'Elena', 'Sofía', 'Valeria', 'Patricia', 'Gabriela']
        apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Hernández', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Vásquez']
        
        condiciones = [
            'Diabetes tipo 2', 'Hipertensión arterial', 'Hipotiroidismo', 'Resistencia a la insulina',
            'Colesterol elevado', 'Triglicéridos elevados', 'Gastritis', 'Colon irritable', ''
        ]
        
        alergias = [
            'Maní', 'Lácteos', 'Gluten', 'Mariscos', 'Huevo', 'Soya', 'Nueces', ''
        ]
        
        pacientes = []
        dnies_usados = set()
        
        for i in range(cantidad):
            sexo = random.choice(['M', 'F'])
            nombre = random.choice(nombres_m if sexo == 'M' else nombres_f)
            apellido1 = random.choice(apellidos)
            apellido2 = random.choice(apellidos)
            
            # Generar DNI único
            while True:
                dni = str(random.randint(10000000, 99999999))
                if dni not in dnies_usados:
                    dnies_usados.add(dni)
                    break
            
            # Fecha de nacimiento (18-65 años)
            edad = random.randint(18, 65)
            fecha_nac = date.today() - timedelta(days=edad * 365 + random.randint(0, 364))
            
            # Peso y talla realistas
            if sexo == 'M':
                peso = Decimal(str(round(random.uniform(60, 110), 2)))
                talla = Decimal(str(round(random.uniform(160, 185), 2)))
            else:
                peso = Decimal(str(round(random.uniform(50, 95), 2)))
                talla = Decimal(str(round(random.uniform(150, 175), 2)))
            
            # Teléfono (9 dígitos)
            telefono = '9' + str(random.randint(10000000, 99999999))
            
            # Email (formato simple y válido)
            email = f'paciente{i+1}@example.com'
            
            paciente = Paciente.objects.create(
                nutricionista=nutricionista,
                nombre=nombre,
                apellido=f'{apellido1} {apellido2}',
                dni=dni,
                fecha_nacimiento=fecha_nac,
                sexo=sexo,
                ocupacion=random.choice(['Oficinista', 'Docente', 'Ingeniero', 'Comerciante', 'Estudiante', 'Ama de casa', 'Médico', 'Abogado']),
                peso=peso,
                talla=talla,
                telefono=telefono,
                email=email,
                direccion=f'Av. {random.choice(["Brasil", "Arequipa", "Tacna", "Salaverry", "Benavides"])} {random.randint(100, 3000)}, Lima',
                condiciones_medicas=random.choice(condiciones),
                alergias=random.choice(alergias),
                notas_generales=f'Motivo de Consulta: {random.choice(["Pérdida de peso", "Ganancia muscular", "Mejorar alimentación", "Control de diabetes"])}\nObservaciones Iniciales:\nPaciente refiere dificultad para mantener dieta.',
                estado=random.choices([True, False], weights=[90, 10])[0],
            )
            pacientes.append(paciente)
        
        return pacientes

    def crear_citas(self, pacientes, nutricionista, meses=6):
        """Crea citas distribuidas en el tiempo usando bulk_create para evitar validaciones"""
        citas_objs = []
        hoy = date.today()
        
        tipos_cita = ['primera_consulta', 'seguimiento', 'control', 'evaluacion']
        estados = ['completada', 'finalizada', 'programada', 'cancelada', 'no_asistio']
        
        motivos = [
            'Control mensual de peso',
            'Primera consulta nutricional',
            'Seguimiento de plan alimentario',
            'Evaluación de composición corporal',
            'Control de diabetes',
            'Ajuste de plan nutricional',
            'Consulta por síntomas digestivos',
            'Control post-operatorio',
        ]
        
        from django.utils.timezone import make_aware
        
        for paciente in pacientes:
            if not paciente.estado:
                continue
            
            num_citas = random.randint(5, 8)
            
            for i in range(num_citas):
                # 60% citas pasadas (últimos 3 meses), 40% futuras (próximos 30 días)
                if random.random() < 0.6:
                    dias_atras = random.randint(1, 90)
                    fecha = hoy - timedelta(days=dias_atras)
                    estado = random.choices(
                        ['completada', 'finalizada', 'cancelada', 'no_asistio'],
                        weights=[35, 35, 15, 15]
                    )[0]
                else:
                    dias_adelante = random.randint(1, 30)
                    fecha = hoy + timedelta(days=dias_adelante)
                    estado = 'programada'
                
                hora = random.randint(8, 17)
                minuto = random.choice([0, 15, 30, 45])
                fecha_hora = make_aware(datetime.combine(fecha, time(hora, minuto)))
                
                tipo = random.choices(tipos_cita, weights=[30, 50, 10, 10])[0]
                duracion = random.choice([45, 60])
                
                if tipo == 'primera_consulta':
                    costo = Decimal(random.choice([120, 150]))
                elif tipo == 'evaluacion':
                    costo = Decimal(random.choice([100, 130]))
                else:
                    costo = Decimal(random.choice([80, 100]))
                
                cita = Cita(
                    paciente=paciente,
                    nutricionista=nutricionista,
                    fecha_hora=fecha_hora,
                    duracion_minutos=duracion,
                    tipo=tipo,
                    estado=estado,
                    motivo=random.choice(motivos),
                    costo=costo,
                )
                citas_objs.append(cita)
        
        Cita.objects.bulk_create(citas_objs, ignore_conflicts=True)
        return citas_objs

    def crear_consultas(self, pacientes, nutricionista):
        """Crea consultas clínicas"""
        consultas = []
        
        tipos_consulta = ['primera_consulta', 'seguimiento', 'control', 'reevaluacion']
        estados_consulta = ['finalizada', 'en_curso']
        
        for paciente in pacientes:
            # 1-3 consultas por paciente
            num_consultas = random.randint(1, 3)
            
            for i in range(num_consultas):
                # Numeración correlativa
                num_consulta = i + 1
                
                # Fecha aleatoria en últimos 3 meses
                dias_atras = random.randint(0, 90)
                fecha = date.today() - timedelta(days=dias_atras)
                
                # Hora aleatoria
                hora = random.randint(8, 17)
                minuto = random.choice([0, 15, 30, 45])
                hora_inicio = time(hora, minuto)
                
                # Estado (mayoría finalizadas)
                estado = random.choices(estados_consulta, weights=[85, 15])[0]
                
                # Tipo
                tipo = random.choice(tipos_consulta)
                
                consulta = Consulta.objects.create(
                    paciente=paciente,
                    numero_consulta=num_consulta,
                    tipo=tipo,
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    estado=estado,
                    profesional=nutricionista,
                    informacion_clinica={
                        'objetivo_principal': random.choice(['Pérdida de grasa', 'Ganancia muscular', 'Mejorar hábitos', 'Control médico']),
                        'habitos': {
                            'actividad_fisica': random.choice(['Sedentario', 'Ligero', 'Moderado', 'Intenso']),
                            'sueno_horas': str(random.randint(5, 9)),
                            'hidratacion': f'{random.uniform(1.5, 3.0):.1f}L',
                        }
                    },
                    evaluacion={
                        'diagnostico_principal': random.choice(['Normopeso', 'Sobrepeso', 'Obesidad grado I', 'Obesidad grado II']),
                        'objetivo_principal': 'Pérdida de grasa',
                    }
                )
                consultas.append(consulta)
        
        return consultas

    def crear_medidas(self, pacientes, consultas):
        """Crea evolución de medidas corporales"""
        medidas = []
        
        for paciente in pacientes:
            # 3-5 mediciones por paciente
            num_mediciones = random.randint(3, 5)
            
            # Peso inicial y objetivo
            peso_inicial = float(paciente.peso)
            talla = float(paciente.talla)
            
            for i in range(num_mediciones):
                # Fecha distribuida en últimos 3 meses
                dias_atras = (num_mediciones - i - 1) * 20 + random.randint(0, 10)
                fecha = date.today() - timedelta(days=dias_atras)
                
                # Peso disminuye gradualmente
                perdida = i * random.uniform(0.5, 2.0)
                peso = max(50, peso_inicial - perdida)
                
                # Buscar consulta asociada si existe
                consulta = random.choice([c for c in consultas if c.paciente == paciente] + [None])
                
                medida = MedidaCorporal.objects.create(
                    paciente=paciente,
                    consulta=consulta,
                    fecha=fecha,
                    peso_kg=Decimal(str(round(peso, 2))),
                    talla_cm=Decimal(str(round(talla, 1))),
                    grasa_corporal_pct=Decimal(str(round(random.uniform(18, 35), 1))),
                    masa_muscular_kg=Decimal(str(round(random.uniform(25, 40), 2))),
                    masa_muscular_pct=Decimal(str(round(random.uniform(25, 40), 1))),
                    cintura_cm=Decimal(str(round(random.uniform(65, 110), 1))),
                    cadera_cm=Decimal(str(round(random.uniform(85, 120), 1))),
                    agua_corporal_pct=Decimal(str(round(random.uniform(45, 60), 1))),
                )
                medidas.append(medida)
        
        return medidas

    def crear_recomendaciones(self, pacientes, nutricionista, consultas):
        """Crea recomendaciones con estados variados"""
        recomendaciones = []
        
        categorias = ['hidratacion', 'actividad_fisica', 'alimentos_recomendados', 'alimentos_limitar', 'generales']
        estados_cumplimiento = ['cumplida', 'parcial', 'no_cumplida', 'pendiente']
        
        descripciones = {
            'hidratacion': {'texto': 'Beber mínimo 2 litros de agua al día', 'detalle': 'Distribuir en 8 vasos'},
            'actividad_fisica': {'texto': 'Caminar 30 minutos diarios', 'detalle': '5 días por semana'},
            'alimentos_recomendados': {'texto': 'Consumir 5 porciones de frutas y verduras', 'detalle': 'Variar colores'},
            'alimentos_limitar': {'texto': 'Reducir consumo de azúcares añadidos', 'detalle': 'Evitar bebidas azucaradas'},
            'generales': {'texto': 'Mantener horarios regulares de comida', 'detalle': '3 comidas principales + 2 snacks'},
        }
        
        for paciente in pacientes:
            # 2-4 recomendaciones por paciente
            num_recomendaciones = random.randint(2, 4)
            
            for categoria in random.sample(categorias, num_recomendaciones):
                # Fecha en últimos 2 meses
                dias_atras = random.randint(0, 60)
                fecha = date.today() - timedelta(days=dias_atras)
                
                # Estado con distribución
                estado = random.choices(
                    estados_cumplimiento,
                    weights=[30, 25, 20, 25]
                )[0]
                
                # Buscar consulta asociada
                consulta = random.choice([c for c in consultas if c.paciente == paciente] + [None])
                
                recomendacion = Recomendacion.objects.create(
                    paciente=paciente,
                    consulta=consulta,
                    nutricionista=nutricionista,
                    categoria=categoria,
                    descripcion=descripciones[categoria],
                    fecha=fecha,
                    estado_cumplimiento=estado,
                )
                recomendaciones.append(recomendacion)
        
        return recomendaciones

    def crear_notas(self, pacientes, nutricionista, consultas):
        """Crea notas clínicas"""
        notas = []
        
        tipos_nota = ['consulta', 'seguimiento', 'evaluacion']
        
        for paciente in pacientes:
            # 1-2 notas por paciente
            num_notas = random.randint(1, 2)
            
            for i in range(num_notas):
                # Fecha en últimos 2 meses
                dias_atras = random.randint(0, 60)
                fecha = date.today() - timedelta(days=dias_atras)
                
                # Buscar consulta asociada
                consulta = random.choice([c for c in consultas if c.paciente == paciente] + [None])
                
                nota = NotaClinica.objects.create(
                    paciente=paciente,
                    consulta=consulta,
                    fecha=fecha,
                    titulo=f'Nota de {random.choice(["control", "seguimiento", "evaluación"])}',
                    motivo_consulta='Control rutinario',
                    resumen_consulta='Paciente acude a control. Se evalúa progreso y se ajustan indicaciones.',
                    objetivos_acordados='Continuar con plan alimentario. Aumentar actividad física.',
                    plan_accion='Próxima cita en 30 días. Mantener registro de alimentos.',
                    tipo=random.choice(tipos_nota),
                )
                notas.append(nota)
        
        return notas
