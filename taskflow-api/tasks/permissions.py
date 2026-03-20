from rest_framework import permissions

class IsProjectParticipant(permissions.BasePermission):
    """
    Permiso que permite ver tareas a propietarios, miembros o asignados del proyecto.
    """
    def has_object_permission(self, request, view, obj):
        project = obj.project
        return (
            project.owner == request.user or 
            project.members.filter(id=request.user.id).exists() or
            obj.assigned_to == request.user
        )

class CanManageTask(permissions.BasePermission):
    """
    Permiso que solo permite al dueño del proyecto o al creador de la tarea editarla/borrarla.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return (
            obj.project.owner == request.user or 
            obj.created_by == request.user
        )

class IsTaskAssignee(permissions.BasePermission):
    """
    Permiso especial: el responsable (asignado) solo puede cambiar el estado de la tarea.
    """
    def has_object_permission(self, request, view, obj):
        # Si es el asignado, pero no el dueño/creador, verificamos qué campos está tocando
        if obj.assigned_to == request.user:
            if request.method in ['PATCH', 'PUT']:
                # Esta lógica de campos se maneja mejor en el perform_update o en el serializer,
                # pero el permiso base permite el acceso al objeto.
                return True
        return False
