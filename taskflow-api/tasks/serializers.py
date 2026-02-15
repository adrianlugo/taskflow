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
        if value is not None:
            try:
                User.objects.get(id=value)
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Usuario no encontrado")
        return value
    
    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        
        if assigned_to_id:
            assigned_to = User.objects.get(id=assigned_to_id)
            validated_data['assigned_to'] = assigned_to
        
        return Task.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
               
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if assigned_to_id is not None:
            if assigned_to_id:
                assigned_to = User.objects.get(id=assigned_to_id)
                instance.assigned_to = assigned_to
            else:
                instance.assigned_to = None
        
        return instance
