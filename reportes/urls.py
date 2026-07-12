from django.urls import path
from . import views
from . import pdf_views

app_name = "reportes"

urlpatterns = [
    path("", views.dashboard_reportes, name="dashboard"),
    path("clinicos/", views.reportes_clinicos, name="clinicos"),
    path("operativos/", views.reportes_operativos, name="operativos"),
    path("financieros/", views.reportes_financieros, name="financieros"),
    path("clinicos/pdf/", pdf_views.pdf_clinicos, name="clinicos_pdf"),
    path("operativos/pdf/", pdf_views.pdf_operativos, name="operativos_pdf"),
    path("financieros/pdf/", pdf_views.pdf_financieros, name="financieros_pdf"),
]
