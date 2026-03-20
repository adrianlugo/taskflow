from rest_framework import permissions

class IsProjectOwner(permissions.BasePermission):
    """
    Permiso que solo permite al propietario del proyecto editarlo o eliminarlo.
    """
    def has_object_permission(self, request, view, obj):
        # El acceso de lectura está permitido para miembros y el owner (manejado en el queryset)
        # Pero las acciones de escritura (PUT, PATCH, DELETE) solo para el owner
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.owner == request.user

class IsProjectMember(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es miembro o propietario del proyecto.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()
