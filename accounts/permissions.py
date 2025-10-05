from rest_framework.permissions import BasePermission
from organizations.models import OrganizationMembership
from .models import RoleChoices
from careteammemberships.models import CareTeamMembershipStatus

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

class IsOrgAdminForCareTeam(BasePermission):
    """
    Verifies if the user is an admin of the managing organization for the care team
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and OrganizationMembership.objects.filter(
                user=request.user,
                organization=view.kwargs.get('organization_id'),
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

class IsPatient(BasePermission):
    """
    Verifies if the user is a patient
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == RoleChoices.PATIENT
        )

class IsClinicianForPatient(BasePermission):
    """
    Verifies if the user is a clinician for the patient
    """
    def has_permission(self, request, view):
        patient_id = view.kwargs.get('patient_id')
        user = request.user
        try:
            # user may not have a clinician profile or a care team membership
            care_team_membership = user.clinician_profile.care_team_memberships.filter(
                patient_id=patient_id,
                status=CareTeamMembershipStatus.ACTIVE
            )
        except:
            # If no care team membership or clinician profile, return False
            return False
        
        return (
            request.user.is_authenticated
            and request.user.role == RoleChoices.CLINICIAN
            and care_team_membership.exists()
        )
