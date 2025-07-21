from rest_framework.permissions import BasePermission

class IsVendorOrReadOnly(BasePermission):
    """
    Only allow vendors to create/update/delete their products.
    Read-only access for others.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS: GET, HEAD, OPTIONS
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return obj.vendor.user == request.user  # Assuming Vendor is linked to User

class IsAdminOrBDA(BasePermission):
    """
    Allow access only to admin or BDA users.
    Adjust the logic below based on your role management system.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
            # OR implement custom role check if you have one.
        )
