from rest_framework import serializers
from .models import Project
from authentication.serializers import UserSerializer
from django.contrib.auth.models import User


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def validate_member_ids(self, value):
        if value:
            existing_users = User.objects.filter(id__in=value)
            if len(existing_users) != len(value):
                found_ids = list(existing_users.values_list('id', flat=True))
                invalid_ids = [uid for uid in value if uid not in found_ids]
                raise serializers.ValidationError(f"Usuarios no encontrados: {invalid_ids}")
        return value
    
    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        # Asignar automáticamente el usuario autenticado como owner
        validated_data['owner'] = self.context['request'].user
        project_as_member = Project.objects.create(**validated_data)
        
        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            project_as_member.members.set(members)
        
        return project_as_member
    
    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if member_ids is not None:
            members = User.objects.filter(id__in=member_ids)
            instance.members.set(members)
        
        return instance
