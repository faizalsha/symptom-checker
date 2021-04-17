from rest_framework.permissions import BasePermission


class IsEmailVerified(BasePermission):
    """
    Permissions for letting authenticated and email verified users only.
    """

    message = "Your email should be verified to perform this action."

    def has_permission(self, request, view):
        # Users email should be verified.
        return bool(request.user.is_email_verified)
