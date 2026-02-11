from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer
from drf_spectacular.utils import extend_schema


class UserListView(generics.ListAPIView):
    """
    Vista para listar todos los usuarios disponibles
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Listar todos los usuarios",
        description="Retorna una lista de todos los usuarios registrados en el sistema",
        tags=["Autenticación"],
        responses={
            200: UserSerializer(many=True),
            401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Iniciar sesión de usuario",
    description="Autentica al usuario y retorna tokens JWT de acceso y refresco",
    operation_id="auth_login",
    tags=["Autenticación"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Nombre de usuario'},
                'password': {'type': 'string', 'description': 'Contraseña del usuario'}
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access': {'type': 'string', 'description': 'Token de acceso JWT'},
                'refresh': {'type': 'string', 'description': 'Token de refresco JWT'},
                'user': {'type': 'object', 'description': 'Datos del usuario autenticado'}
            }
        },
        401: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Mensaje de error'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    else:
        return Response(
            {'error': 'Credenciales inválidas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    summary="Obtener perfil de usuario",
    description="Retorna el perfil extendido del usuario autenticado",
    tags=["Autenticación"],
    responses={
        200: ProfileSerializer,
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}
    }
)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    @extend_schema(
        summary="Actualizar perfil de usuario",
        description="Actualiza el perfil extendido del usuario autenticado",
        operation_id="auth_profile_update",
        tags=["Autenticación"],
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}}
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar parcialmente perfil de usuario",
        description="Actualiza parcialmente el perfil extendido del usuario autenticado",
        operation_id="auth_profile_partial_update",
        tags=["Autenticación"],
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}}
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    summary="Obtener datos del usuario actual",
    description="Retorna información básica del usuario autenticado",
    operation_id="auth_user_current",
    tags=["Autenticación"],
    responses={
        200: UserSerializer,
        401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}}
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario en el sistema",
    operation_id="auth_register",
    tags=["Autenticación"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Nombre de usuario único'},
                'email': {'type': 'string', 'description': 'Correo electrónico'},
                'password': {'type': 'string', 'description': 'Contraseña'},
                'password_confirm': {'type': 'string', 'description': 'Confirmación de contraseña'}
            },
            'required': ['username', 'email', 'password', 'password_confirm']
        }
    },
    responses={
        201: {
            'type': 'object',
            'properties': {
                'user': {'type': 'object', 'description': 'Datos del usuario creado'},
                'message': {'type': 'string', 'description': 'Mensaje de éxito'}
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Mensaje de error'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    
    # Validaciones básicas
    if not username or not email or not password or not password_confirm:
        return Response(
            {'error': 'Todos los campos son requeridos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if password != password_confirm:
        return Response(
            {'error': 'Las contraseñas no coinciden'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'El nombre de usuario ya existe'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'El email ya está registrado'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear usuario
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    return Response({
        'user': UserSerializer(user).data,
        'message': 'Usuario creado exitosamente'
    }, status=status.HTTP_201_CREATED)
