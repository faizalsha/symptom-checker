from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    """
    Permissions of user to access their own data, and 
    allowing any one to registering themselves.
    """

    def has_permission(self, request, view):
        # Allowing users registering themselves.
        if request.method == 'POST':
            return True

        # For all other operations User mush be authenticated.
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allowing access to user's only to access their own data.
        return bool(request.user == obj)
