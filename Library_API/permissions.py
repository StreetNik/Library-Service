from rest_framework import permissions


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to anyone and POST only for superusers.
    """

    def has_permission(self, request, view):
        # Allow GET requests for anyone
        if request.method == "GET":
            return True

        # Allow POST requests only for superusers
        return request.user.is_superuser
