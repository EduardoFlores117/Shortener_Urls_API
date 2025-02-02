from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """Permiso personalizado para permitir solo a los dueños o administradores editar y eliminar URLs."""
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.owner == request.user
