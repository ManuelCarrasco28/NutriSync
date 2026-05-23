import threading

_thread_locals = threading.local()


def get_current_request():
    """Obtiene la petición HTTP actual en el contexto de ejecución del hilo."""
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """Obtiene el usuario autenticado de la petición actual."""
    request = get_current_request()
    if request:
        return request.user
    return None


class ThreadLocalRequestMiddleware:
    """
    Middleware que guarda la petición HTTP en una variable local al hilo.
    Permite acceder al request y al usuario autenticado desde formularios,
    modelos o validadores sin necesidad de pasarlos explícitamente por las vistas.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            if hasattr(_thread_locals, "request"):
                del _thread_locals.request
        return response
