"""
Vistas personalizadas para JWT con documentación mejorada
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Refrescar token de acceso",
    description="""
    Obtiene un nuevo token de acceso JWT usando un token de refresco válido.
    
    **Uso:**
    1. Usa el token 'refresh' obtenido en el login
    2. Envía este token en el cuerpo de la solicitud
    3. Recibirás un nuevo token 'access' válido
    
    **Importante:** El token de refresco puede expirar. Si expira, necesitarás hacer login nuevamente.
    """,
    operation_id="auth_refresh_token",
    tags=["Autenticacion"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {
                    'type': 'string', 
                    'description': 'Token de refresco JWT obtenido en el login',
                    'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                }
            },
            'required': ['refresh']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access': {
                    'type': 'string', 
                    'description': 'Nuevo token de acceso JWT válido por 60 minutos',
                    'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                },
                'refresh': {
                    'type': 'string', 
                    'description': 'Nuevo token de refresco (si la rotación está activada)',
                    'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                }
            }
        },
        401: {
            'type': 'object',
            'properties': {
                'detail': {
                    'type': 'string',
                    'description': 'El token de refresco es inválido, ha expirado o fue revocado',
                    'example': 'Token de refresco inválido o expirado'
                },
                'code': {
                    'type': 'string',
                    'description': 'Código de error para depuración',
                    'example': 'token_not_valid'
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {
                    'type': 'string',
                    'description': 'Error en el formato de la solicitud o token faltante',
                    'example': 'El token de refresco es requerido'
                }
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Vista personalizada para refrescar tokens JWT con documentación mejorada
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'El token de refresco es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        
        data = {
            'access': str(access_token),
        }
        
        # Si está configurado para rotar tokens, incluir nuevo refresh
        if hasattr(refresh, 'access_token'):
            try:
                data['refresh'] = str(refresh)
            except:
                pass
        
        return Response(data, status=status.HTTP_200_OK)
        
    except (InvalidToken, TokenError) as e:
        return Response(
            {
                'detail': 'Token de refresco inválido o expirado',
                'code': 'token_not_valid'
            }, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'error': f'Error al procesar el token: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(exclude=True)
class HiddenTokenRefreshView(TokenRefreshView):
    """
    Mantiene el endpoint funcional pero oculto en la documentación.
    """
    pass
