from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    #Только админ может создавать/редактировать/удалять
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff


class IsSelfOrAdmin(BasePermission):
    #Пользователь может управлять только собой. Админ — всеми
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class IsOwnerOrAdmin(BasePermission):
    #Только владелец объекта или админ может редактировать/удалять
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


class IsOwnerCanEditOnly(BasePermission):
    #Владелец может создавать/редактировать, но не удалять
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.method in ('PUT', 'PATCH'):
            return obj.booking.user == request.user
        if request.method == 'DELETE':
            return request.user.is_staff
        return True
