from rest_framework import permissions

class IsOverallAdmin(permissions.BasePermission):
    """
    Custom permission: only users whose role == 'Overall_Admin' are allowed
    non-safe-method requests (POST, PUT, PATCH, DELETE).
    SAFE_METHODS (GET, HEAD, OPTIONS) remain available to any authenticated user.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "Overall_Admin"
        )