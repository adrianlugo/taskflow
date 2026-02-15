from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer
from projects.models import Project
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Listar tareas del usuario",
    description="Retorna todas las tareas donde el usuario es propietario, miembro o asignado del proyecto",
    tags=["Tareas"],
    responses={
        200: TaskSerializer(many=True),
        401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
        403: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Permiso denegado'}}}
    }
)
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        queryset = Task.objects.filter(
            models.Q(project__owner=self.request.user) | 
            models.Q(project__members=self.request.user) |
            models.Q(assigned_to=self.request.user)
        ).distinct()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    @extend_schema(
        summary="Crear nueva tarea",
        description="Crea una nueva tarea en un proyecto específico",
        operation_id="tasks_create",
        tags=["Tareas"],
        request=TaskSerializer,
        responses={
            201: TaskSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            403: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Permiso denegado'}}}
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = get_object_or_404(Project, id=project_id)
        
        # Security check: Only project owner or members can create tasks
        if project.owner != self.request.user and self.request.user not in project.members.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para crear tareas en este proyecto")
        
        serializer.save(created_by=self.request.user, project=project)


@extend_schema(
    summary="Obtener detalles de tarea",
    description="Retorna información detallada de una tarea específica",
    tags=["Tareas"],
    responses={
        200: TaskSerializer,
        401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
        404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Tarea no encontrada'}}}
    }
)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(
            models.Q(project__owner=self.request.user) | 
            models.Q(project__members=self.request.user) |
            models.Q(assigned_to=self.request.user)
        ).distinct()
    
    @extend_schema(
        summary="Actualizar tarea",
        description="Actualiza completamente una tarea específica",
        operation_id="tasks_detail_update",
        tags=["Tareas"],
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Tarea no encontrada'}}}
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar parcialmente tarea",
        description="Actualiza parcialmente una tarea específica",
        operation_id="tasks_detail_partial_update",
        tags=["Tareas"],
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Tarea no encontrada'}}}
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Eliminar tarea",
        description="Elimina una tarea específica permanentemente",
        operation_id="tasks_detail_delete",
        tags=["Tareas"],
        responses={
            204: {'description': 'Tarea eliminada exitosamente'},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            404: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Tarea no encontrada'}}}
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Listar comentarios de tarea",
    description="Retorna todos los comentarios de una tarea específica",
    tags=["Tareas"],
    responses={
        200: TaskCommentSerializer(many=True),
        401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
        403: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Permiso denegado'}}}
    }
)
class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskComment.objects.filter(task_id=task_id)
    
    @extend_schema(
        summary="Crear comentario en tarea",
        description="Crea un nuevo comentario en una tarea específica",
        operation_id="tasks_create_comment",
        tags=["Tareas"],
        request=TaskCommentSerializer,
        responses={
            201: TaskCommentSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Mensaje de error'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'No autorizado'}}},
            403: {'type': 'object', 'properties': {'detail': {'type': 'string', 'description': 'Permiso denegado'}}}
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        
        if (task.project.owner != self.request.user and 
            self.request.user not in task.project.members.all() and 
            task.assigned_to != self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para comentar en esta tarea")
        
        serializer.save(task=task, author=self.request.user)


@extend_schema(
    summary="Asignar tarea a usuario",
    description="Asigna una tarea específica a un usuario (solo propietario o miembros del proyecto)",
    operation_id="tasks_assign",
    tags=["Tareas"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID del usuario al que se asignará la tarea'}
            },
            'required': ['user_id']
        }
    },
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string', 'description': 'Mensaje de éxito'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Permiso denegado'}}},
        404: {'type': 'object', 'properties': {'error': {'type': 'string', 'description': 'Tarea o usuario no encontrado'}}}
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if (task.project.owner != request.user and 
        request.user not in task.project.members.all()):
        return Response(
            {'error': 'No tienes permiso para asignar esta tarea'}, 
            status=status.HTTP_403_FORBIDDEN # type: ignore
        )
    
    user_id = request.data.get('user_id')
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        task.assigned_to = user
        task.save()
        return Response({'message': 'Task assigned successfully'})
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND # type: ignore
        )

