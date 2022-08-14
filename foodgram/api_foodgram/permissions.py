from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.user.is_admin()
                or request.user.is_staff()
                or request.user == obj.author
                or request.method in permissions.SAFE_METHODS
            )
        return request.method in permissions.SAFE_METHODS
