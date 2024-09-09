from rest_framework import permissions

class IsViewUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access if method is GET and user is authenticated with 'view' role
        if request.method == 'GET':
            return request.user.is_authenticated and request.user.accountmembership_set.filter(role='view').exists()
        return False

class IsPostOnlyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access if method is POST and user is authenticated with 'post' role
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.accountmembership_set.filter(role='post').exists()
        return False

class IsCRUDUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access if method is POST, PATCH, or DELETE and user is authenticated with 'crud' role
        if request.method in ['POST', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.accountmembership_set.filter(role='crud').exists()
        return False
