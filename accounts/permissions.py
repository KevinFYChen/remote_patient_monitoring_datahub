from rest_framework.permissions import BasePermission
from organizations.models import OrganizationMembership

class IsOrganizationAdminForOrg(BasePermission):
    """
    Verifies if the user is an organization admin
    """
    def has_permission(self, request, view):
        org_id = view.kwargs.get('organization_id')
        return (
            org_id is not None 
            and OrganizationMembership.objects.filter(
                user=request.user,
                organization=org_id,
                status='active',
                role='admin'
            ).exists()
            and request.user.is_authenticated
            
        )