from rest_framework.permissions import BasePermission
from organizations.models import OrganizationMembership
from .models import RoleChoices

class IsOrganizationAdminForOrg(BasePermission):
    """
    Verifies if the user is an organization admin
    """
    def has_permission(self, request, view):
        org_id = view.kwargs.get('organization_id')
        return (
            org_id is not None 
            and request.user.is_authenticated
            and OrganizationMembership.objects.filter(
                user=request.user,
                organization=org_id,
                status='active',
                role='admin'
            ).exists()
        )

class IsOrganizationAdmin(BasePermission):
    """
    Verifies if the user is an organization admin
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and OrganizationMembership.objects.filter(
                user=request.user,
                status='active',
                role='admin'
            ).exists()
        )

class IsClinician(BasePermission):
    """
    Verifies if the user is a clinician
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == RoleChoices.CLINICIAN
        )
