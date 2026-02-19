"""
Vistas principales para la página de bienvenida de la API
"""
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="Página principal de la API",
    description="Retorna información completa sobre la TaskFlow API y todos sus endpoints disponibles",
    tags=["General"],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'title': {'type': 'string', 'description': 'Nombre de la API'},
                'version': {'type': 'string', 'description': 'Versión actual'},
                'description': {'type': 'string', 'description': 'Descripción de la API'},
                'status': {'type': 'string', 'description': 'Estado actual de la API'},
                'endpoints': {
                    'type': 'object',
                    'properties': {
                        'documentación': {
                            'type': 'object',
                            'properties': {
                                'swagger_ui': {'type': 'string', 'description': 'URL de Swagger UI'},
                                'redoc': {'type': 'string', 'description': 'URL de ReDoc'},
                                'schema_json': {'type': 'string', 'description': 'URL del schema OpenAPI'}
                            }
                        },
                        'autenticación': {
                            'type': 'object',
                            'properties': {
                                'register': {'type': 'string', 'description': 'URL de registro'},
                                'login': {'type': 'string', 'description': 'URL de login'},
                                'refresh': {'type': 'string', 'description': 'URL de refresh token'},
                                'profile': {'type': 'string', 'description': 'URL de perfil'},
                                'user': {'type': 'string', 'description': 'URL de usuario actual'}
                            }
                        },
                        'proyectos': {
                            'type': 'object',
                            'properties': {
                                'list': {'type': 'string', 'description': 'URL de listado de proyectos'},
                                'detail': {'type': 'string', 'description': 'URL de detalle de proyecto'},
                                'add_member': {'type': 'string', 'description': 'URL para agregar miembro'},
                                'remove_member': {'type': 'string', 'description': 'URL para eliminar miembro'}
                            }
                        },
                        'tareas': {
                            'type': 'object',
                            'properties': {
                                'list': {'type': 'string', 'description': 'URL de listado de tareas'},
                                'detail': {'type': 'string', 'description': 'URL de detalle de tarea'},
                                'comments': {'type': 'string', 'description': 'URL de comentarios'},
                                'assign': {'type': 'string', 'description': 'URL de asignación'}
                            }
                        }
                    }
                },
                'guía_rápida': {
                    'type': 'object',
                    'properties': {
                        '1_registro': {'type': 'string', 'description': 'Paso 1: Registro'},
                        '2_login': {'type': 'string', 'description': 'Paso 2: Inicio de sesion'},
                        '3_usar_token': {'type': 'string', 'description': 'Paso 3: Usar token'},
                        '4_crear_proyecto': {'type': 'string', 'description': 'Paso 4: Crear proyecto'},
                        '5_crear_tarea': {'type': 'string', 'description': 'Paso 5: Crear tarea'}
                    }
                }
            }
        }
    }
)
def api_welcome(request):
    """
    Página de bienvenida de la TaskFlow API
    Muestra todos los enlaces importantes de la API
    """
    base_url = request.build_absolute_uri('/')
    
    api_info = {
        "title": "TaskFlow API - Gestor de Tareas Colaborativo",
        "version": "1.0.0",
        "description": "API REST para gestión de tareas colaborativas tipo Trello/Asana",
        "status": "online",
        "endpoints": {
            "documentación": {
                "swagger_ui": f"{base_url}api/docs/",
                "redoc": f"{base_url}api/redoc/",
                "schema_json": f"{base_url}api/schema/",
                "description": "Documentación interactiva de la API"
            },
            "autenticación": {
                "register": f"{base_url}api/auth/register/",
                "login": f"{base_url}api/auth/login/",
                "refresh": f"{base_url}api/auth/refresh/",
                "profile": f"{base_url}api/auth/profile/",
                "user": f"{base_url}api/auth/user/",
                "description": "Gestión de usuarios y autenticación JWT"
            },
            "proyectos": {
                "list": f"{base_url}api/projects/",
                "detail": f"{base_url}api/projects/{{id}}/",
                "add_member": f"{base_url}api/projects/{{id}}/members/",
                "remove_member": f"{base_url}api/projects/{{id}}/members/{{user_id}}/",
                "description": "Gestión de proyectos y miembros"
            },
            "tareas": {
                "list": f"{base_url}api/tasks/",
                "detail": f"{base_url}api/tasks/{{id}}/",
                "comments": f"{base_url}api/tasks/{{id}}/comments/",
                "assign": f"{base_url}api/tasks/{{id}}/assign/",
                "description": "Gestión de tareas, comentarios y asignaciones"
            }
        },
        "guía_rápida": {
            "1_registro": "POST /api/auth/register/ - Crea una cuenta",
            "2_login": "POST /api/auth/login/ - Obtén tokens JWT",
            "3_usar_token": "Usa el boton 'Autorizar' en /api/docs/ con tu token",
            "4_crear_proyecto": "POST /api/projects/ - Crea tu primer proyecto",
            "5_crear_tarea": "POST /api/tasks/ - Añade tareas al proyecto"
        },
        "autenticación": {
            "tipo": "JWT Bearer Token",
            "formato": "Authorization: Bearer tu_access_token",
            "duración": "Access: 60 min, Refresh: 7 días"
        },
        "links_útiles": {
            "documentación_completa": f"{base_url}api/docs/",
            "documentación_re_doc": f"{base_url}api/redoc/",
            "admin_django": f"{base_url}admin/",
            "github": "https://github.com/tu-usuario/taskflow-api"
        }
    }
    
    return Response(api_info)


@require_http_methods(["GET"])
@extend_schema(
    summary="Verificacion de estado de la API",
    description="Verifica que la API esté funcionando correctamente",
    tags=["General"],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'description': 'Estado de la API'},
                'api': {'type': 'string', 'description': 'Nombre de la API'},
                'version': {'type': 'string', 'description': 'Versión actual'}
            }
        }
    }
)
def health_check(request):
    """
    Endpoint simple para verificar que la API está funcionando
    """
    return JsonResponse({
        "status": "healthy",
        "api": "TaskFlow API",
        "version": "1.0.0"
    })
