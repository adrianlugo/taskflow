from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Project
from .serializers import ProjectSerializer
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(
    summary="Listar proyectos del usuario",
    description="Retorna todos los proyectos donde el usuario es owner o miembro",
    tags=["Proyectos"],
    responses={
        200: ProjectSerializer(many=True),
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}
    }
)
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user)
        ).distinct()
    
    @extend_schema(
        summary="Crear nuevo proyecto",
        description="Crea un nuevo proyecto con el usuario actual como propietario",
        operation_id="projects_create",
        tags=["Proyectos"],
        request=ProjectSerializer,
        responses={
            201: ProjectSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}}
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(
    summary="Obtener detalles de proyecto",
    description="Retorna información detallada de un proyecto específico",
    tags=["Proyectos"],
    responses={
        200: ProjectSerializer,
        401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
        404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Proyecto no encontrado'}}}
    }
)
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user)
        ).distinct()
    
    @extend_schema(
        summary="Actualizar proyecto",
        description="Actualiza completamente un proyecto específico",
        operation_id="projects_detail_update",
        tags=["Proyectos"],
        request=ProjectSerializer,
        responses={
            200: ProjectSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Proyecto no encontrado'}}}
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar parcialmente proyecto",
        description="Actualiza parcialmente un proyecto específico",
        operation_id="projects_detail_partial_update",
        tags=["Proyectos"],
        request=ProjectSerializer,
        responses={
            200: ProjectSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Proyecto no encontrado'}}}
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Eliminar proyecto",
        description="Elimina un proyecto específico permanentemente",
        operation_id="projects_detail_delete",
        tags=["Proyectos"],
        responses={
            204: {'description': 'Proyecto eliminado exitosamente'},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Proyecto no encontrado'}}}
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Agregar miembro al proyecto",
    description="Agrega un usuario como miembro de un proyecto (solo el propietario puede hacerlo)",
    operation_id="projects_add_member",
    tags=["Proyectos"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID del usuario a agregar como miembro'}
            },
            'required': ['user_id']
        }
    },
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string', 'description': 'Mensaje de éxito'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Permiso denegado'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Usuario no encontrado'}}}
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_project_member(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        return Response(
            {'error': 'Solo el owner del proyecto puede agregar miembros'}, 
            status=403
        )
    
    user_id = request.data.get('user_id')
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        project.members.add(user)
        return Response({'message': 'Miembro agregado exitosamente'})
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)


@extend_schema(
    summary="Eliminar miembro del proyecto",
    description="Elimina un usuario como miembro de un proyecto (solo el propietario puede hacerlo)",
    operation_id="projects_remove_member",
    tags=["Proyectos"],
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string', 'description': 'Mensaje de éxito'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Permiso denegado'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Usuario no encontrado'}}}
    }
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_project_member(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        return Response(
            {'error': 'Solo el owner del proyecto puede eliminar miembros'}, 
            status=403
        )
    
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        project.members.remove(user)
        return Response({'message': 'Miembro eliminado exitosamente'})
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_available_users(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Solo el owner puede ver usuarios disponibles
    if project.owner != request.user:
        return Response({'error': 'No autorizado'}, status=403)

    from django.contrib.auth.models import User

    # Excluir usuarios que ya son miembros
    users = User.objects.exclude(id__in=project.members.all())

    data = [
        {
            'id': u.id,
            'username': u.username,
            'email': u.email
        }
        for u in users
    ]

    return Response({'success': True, 'users': data})
