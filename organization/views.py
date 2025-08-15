import re
from django.shortcuts import render
from rest_framework import generics, permissions
from accounts.permissions import IsOrganizationAdminForOrg
from organization.models import Organization, ClinicianInvitation
from datetime import timedelta, datetime, timezone
from rest_framework.response import Response

class SendClinicianInvitationView(generics.CreateAPIView):
    """
    Creates an invitation for a clinician to create an account in an organization
    """
    permission_classes = [permissions.IsAuthenticated & IsOrganizationAdminForOrg]
    serializer_class = ClinicianInvitationSerializer

    def post(self, request, *args, **kwargs):
        """
        Create an invitation for a clinician to create an account in an organization
        """
        # Expiration time is 1 day from now, in UTC
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=1)
        clinician_email = request.data.get('clinician_email')
        # verify that this is a valid email
        if not is_valid_email(clinician_email):
            return Response({'error': 'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)
        
        organization_id = kwargs.get('organization_id')
        organization = Organization.objects.get(id=organization_id)
        invited_by = request.user
        status = 'pending'

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None





