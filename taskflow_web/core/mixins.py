from django.shortcuts import redirect
from django.urls import reverse_lazy

__all__ = ['LoginRequiredMixin']


class LoginRequiredMixin:
    """
    Verifica que el usuario esté autenticado antes de acceder a la vista.
    
    Redirige a la página de login si no hay token JWT en la sesión.
    Preserva la URL original con el parámetro `next` para volver tras el login.
    """

    def dispatch(self, request, *args, **kwargs):
        token = request.session.get('access')
        if not token:
            return redirect(f"{reverse_lazy('authentication:login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)
