from rest_framework import serializers
from .models import Task, TaskComment
from projects.serializers import ProjectSerializer
from projects.models import Project
from authentication.serializers import UserSerializer
from django.contrib.auth.models import User


class TaskCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ('task', 'author')


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True
    )
    project_detail = ProjectSerializer(source='project', read_only=True)
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'project': {'write_only': True}
        }
    
    def validate_assigned_to_id(self, value):
        # Permitir valores nulos/"vacíos" para desasignar
        if value in (None, '', 0):
            return None
        # Validar que el usuario exista
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        # Determinar el proyecto en contexto (create/update)
        project_id = self.initial_data.get('project')
        project = None
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                raise serializers.ValidationError("Proyecto no válido para la asignación")
        elif self.instance:
            project = self.instance.project
        # Si hay proyecto, el usuario asignado debe pertenecer
        if project and (user != project.owner and user not in project.members.all()):
            raise serializers.ValidationError("El usuario no pertenece al proyecto")
        return value
    
    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        project = validated_data.get('project')

        if assigned_to_id:
            assigned_to = User.objects.get(id=assigned_to_id)
            if project and (assigned_to != project.owner and assigned_to not in project.members.all()):
                raise serializers.ValidationError("El usuario no pertenece al proyecto")
            validated_data['assigned_to'] = assigned_to

        task = Task.objects.create(**validated_data)
        return task
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        assigned_to_id = validated_data.pop('assigned_to_id', None)

        # Si se cambia la asignación, validar permisos: owner del proyecto o creador
        if assigned_to_id is not None and request:
            project = instance.project
            if request.user != project.owner and request.user != instance.created_by:
                raise serializers.ValidationError({"assigned_to_id": "Solo el propietario del proyecto o el creador de la tarea pueden asignar o reasignar tareas"})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Aplicar cambio de asignación
        if assigned_to_id is not None:
            if assigned_to_id:
                assigned_to = User.objects.get(id=assigned_to_id)
                if assigned_to != instance.project.owner and assigned_to not in instance.project.members.all():
                    raise serializers.ValidationError("El usuario no pertenece al proyecto")
                instance.assigned_to = assigned_to
            else:
                instance.assigned_to = None

        instance.save()
        return instance
