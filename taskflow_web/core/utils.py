__all__ = ['add_form_errors', 'handle_api_auth_error']

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from core.api import API

def add_form_errors(form, result):
    """
    Mapea errores devueltos por la API sobre un formulario Django.
 
    Args:
        form (forms.Form): Instancia del formulario Django donde se aplicarán los errores.
        result (dict|str|list): Respuesta de error de la API (estilo DRF) o mensaje genérico.
 
    Comportamiento:
        - Si `result` es un dict, asigna errores por campo y errores no asociados a campo.
        - Si `result` no es un dict, lo añade como error general del formulario.
    """
    if isinstance(result, dict):
        for field, errors in result.items():
            msg = errors[0] if isinstance(errors, (list, tuple)) else errors

            if field in form.fields:
                form.add_error(field, str(msg))
            else:
                form.add_error(None, str(msg))
    else:
        form.add_error(None, str(result))


def handle_api_auth_error(request, result):
    """
    Si la API responde con error de autenticación, cerrar sesión y redirigir a login.
    Devuelve un redirect o None.
    """
    if API.is_auth_error(result):
        API.logout(request)
        messages.warning(request, 'Tu sesión expiró. Inicia sesión de nuevo.')
        login_url = reverse_lazy('authentication:login')
        return redirect(f"{login_url}?next={request.path}")
    return None
