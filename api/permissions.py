from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin()

class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_manager() or request.user.is_admin())

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin() or obj.created_by == request.user 