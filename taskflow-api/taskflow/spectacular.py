"""
Hooks personalizados para drf-spectacular
"""
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.drainage import warn


def preprocess_remove_endpoints(endpoints, **kwargs):
    """
    Hook para eliminar endpoints problemáticos de la documentación
    """
    # Filtrar endpoints que causan problemas con serializers
    filtered_endpoints = []
    
    for path, path_regex, method, callback in endpoints:
        # Verificar si es una vista que causa problemas
        if (hasattr(callback, 'view_class') and 
            hasattr(callback.view_class, '__name__') and
            'api_welcome' in callback.view_class.__name__):
            # Saltar este endpoint
            continue
        elif path in ['/', '/health/', '/api/health/']:
            # Saltar endpoints principales
            continue
        else:
            # Mantener este endpoint
            filtered_endpoints.append((path, path_regex, method, callback))
    
    return filtered_endpoints
