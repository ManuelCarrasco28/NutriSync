from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse
from django.db.models import Q
from pacientes.models import Paciente
from ..models import PlanNutricional, ComidaPlan, Alimento
from ..forms import PlanNutricionalForm, ComidaPlanForm
from config.choices import DiaSemana, TipoComida, Objetivo

ORDEN_DIAS = [
    DiaSemana.LUNES,
    DiaSemana.MARTES,
    DiaSemana.MIERCOLES,
    DiaSemana.JUEVES,
    DiaSemana.VIERNES,
    DiaSemana.SABADO,
    DiaSemana.DOMINGO,
]

class PlanListView(LoginRequiredMixin, ListView):
    """
    Lista de todos los planes nutricionales del nutricionista.
    Filtramos por paciente__nutricionista para aislamiento de datos.
    """
    model = PlanNutricional
    template_name = "nutricion/planes.html"
    context_object_name = "planes"
    paginate_by = 20

    def get_queryset(self):
        qs = PlanNutricional.objects.select_related("paciente").filter(
            paciente__nutricionista=self.request.user
        )
        estado = self.request.GET.get("estado", "")
        if estado == "activo":
            qs = qs.filter(estado=True)
        elif estado == "inactivo":
            qs = qs.filter(estado=False)

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(paciente__nombre__icontains=q)
                | Q(paciente__apellido__icontains=q)
            )
        return qs.order_by("-fecha_creacion")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["filtro_estado"] = self.request.GET.get("estado", "")
        context["pacientes_disponibles"] = Paciente.objects.filter(
            nutricionista=self.request.user, estado=True
        ).order_by("apellido", "nombre")
        return context


class PlanCreateView(LoginRequiredMixin, CreateView):
    """
    Crea un plan nutricional para un paciente específico.
    El paciente_pk viene de la URL.
    """
    model = PlanNutricional
    form_class = PlanNutricionalForm
    template_name = "nutricion/plan_form.html"

    def get_paciente(self):
        return get_object_or_404(
            Paciente, pk=self.kwargs["paciente_pk"], nutricionista=self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["paciente"] = self.get_paciente()
        return kwargs

    def form_valid(self, form):
        form.instance.paciente = self.get_paciente()
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Plan «{self.object.nombre}» creado correctamente para {self.object.paciente.nombre_completo}.",
        )
        return response

    def get_success_url(self):
        return reverse("nutricion:plan_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paciente"] = self.get_paciente()
        context["titulo"] = "Nuevo Plan Nutricional"
        context["accion"] = "Crear plan"
        return context


class PlanDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada del plan nutricional organizada por días de la semana.
    """
    model = PlanNutricional
    template_name = "nutricion/plan_detalle.html"
    context_object_name = "plan"

    def get_queryset(self):
        return PlanNutricional.objects.select_related("paciente").filter(
            paciente__nutricionista=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = self.object

        comidas = plan.comidas.prefetch_related("alimentos_sugeridos").order_by(
            "dia_semana", "tipo_comida"
        )

        comidas_por_dia = {}
        for dia_key in ORDEN_DIAS:
            comidas_dia = [c for c in comidas if c.dia_semana == dia_key]
            if comidas_dia:
                dia_label = dict(DiaSemana.CHOICES).get(dia_key, dia_key)
                comidas_por_dia[dia_label] = comidas_dia

        context["comidas_por_dia"] = comidas_por_dia
        context["total_comidas"] = comidas.count()

        calorias_total = sum(c.calorias_estimadas for c in comidas)
        context["calorias_total_plan"] = calorias_total
        context["comida_form"] = ComidaPlanForm(user=self.request.user, plan=plan)
        return context


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    """Edición de los datos generales del plan nutricional."""
    model = PlanNutricional
    form_class = PlanNutricionalForm
    template_name = "nutricion/plan_form.html"

    def get_queryset(self):
        return PlanNutricional.objects.select_related("paciente").filter(
            paciente__nutricionista=self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["paciente"] = self.object.paciente
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f"Plan «{self.object.nombre}» actualizado correctamente."
        )
        return response

    def get_success_url(self):
        return reverse("nutricion:plan_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paciente"] = self.object.paciente
        context["titulo"] = "Editar Plan Nutricional"
        context["accion"] = "Guardar cambios"
        return context


@login_required
@require_POST
def plan_toggle_estado(request, pk):
    """
    Activa o desactiva un plan nutricional.
    """
    plan = get_object_or_404(
        PlanNutricional, pk=pk, paciente__nutricionista=request.user
    )

    if not plan.estado:
        PlanNutricional.objects.filter(paciente=plan.paciente, estado=True).update(
            estado=False
        )
        plan.estado = True
        plan.save()
        messages.success(
            request,
            f"Plan «{plan.nombre}» activado. Los otros planes del paciente fueron desactivados.",
        )
    else:
        plan.estado = False
        plan.save()
        messages.success(request, f"Plan «{plan.nombre}» desactivado correctamente.")

    return redirect("nutricion:plan_detalle", pk=plan.pk)


@login_required
@require_POST
def comida_crear(request, plan_pk):
    """
    Agrega una nueva comida a un plan nutricional existente.
    """
    plan = get_object_or_404(
        PlanNutricional, pk=plan_pk, paciente__nutricionista=request.user
    )
    form = ComidaPlanForm(request.POST, user=request.user, plan=plan)

    if form.is_valid():
        comida = form.save(commit=False)
        comida.plan = plan
        comida.save()
        form.save_m2m()
        messages.success(
            request,
            f"Comida «{comida.get_tipo_comida_display()}» del {comida.get_dia_semana_display()} agregada correctamente.",
        )
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{error}")

    return redirect("nutricion:plan_detalle", pk=plan_pk)


@login_required
@require_POST
def comida_eliminar(request, pk):
    """Elimina una comida de un plan nutricional."""
    comida = get_object_or_404(
        ComidaPlan, pk=pk, plan__paciente__nutricionista=request.user
    )
    plan_pk = comida.plan.pk
    nombre = f"{comida.get_tipo_comida_display()} del {comida.get_dia_semana_display()}"
    comida.delete()
    messages.success(request, f"Comida «{nombre}» eliminada correctamente.")
    return redirect("nutricion:plan_detalle", pk=plan_pk)
