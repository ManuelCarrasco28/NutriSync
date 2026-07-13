# administracion/urls.py
# Rutas del panel de administración.

from django.urls import path
from administracion.views import auth, dashboard

app_name = "administracion"

urlpatterns = [
    path("login/",    auth.admin_login_view,    name="login"),
    path("register/", auth.admin_register_view, name="register"),
    path("logout/",   auth.admin_logout_view,   name="logout"),
    path("",          dashboard.dashboard_view, name="dashboard"),
]

