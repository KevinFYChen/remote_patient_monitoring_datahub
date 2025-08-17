import re
from django.shortcuts import render
from django.urls import reverse
from rest_framework import generics, permissions
from accounts.permissions import IsOrganizationAdminForOrg
from .models import Organization, ClinicianInvitation, OrganizationMembership
from datetime import timedelta, datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClinicianInvitationSerializer, OrganizationSerializer
from rest_framework.viewsets import ModelViewSet


class OrganizationViewSet(ModelViewSet):
    """
    Viewset for the Organization model
    """
    lookup_field = 'record_id'
    lookup_url_kwarg = 'organization_id'
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]

class SendClinicianInvitationView(generics.ListCreateAPIView):
    """
    Creates an invitation for a clinician to create an account in an organization
    """
    permission_classes = [permissions.IsAuthenticated & IsOrganizationAdminForOrg]
    serializer_class = ClinicianInvitationSerializer

    def post(self, request, *args, **kwargs):
        """
        Create an invitation for a clinician to create an account in an organization
        """
        clinician_email = request.data.get('clinician_email')
        organization_id = kwargs.get('organization_id')
        # check if the invitation already exists
        if ClinicianInvitation.objects.filter(
            clinician_email=clinician_email,
            organization_id=organization_id,
            status='pending',
            expires_at__gt=datetime.now(tz=timezone.utc)
        ).exists():
            return Response({'error': 'Invitation already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the clinician already has an account
        if OrganizationMembership.objects.filter(
            user__email=clinician_email,
            organization_id=organization_id,
            status__in=['active', 'pending']
        ).exists():
            return Response({'error': 'Clinician already has an account'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Expiration time is 1 day from now, in UTC
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=1)

        invitation_obj = ClinicianInvitation(
            expires_at=expires_at,
            clinician_email=clinician_email,
            organization_id=organization_id,
            invited_by=request.user,
            status='pending'
        )
        # validate the invitation object and save it
        invitation_obj.full_clean()
        invitation_obj.save()

        # send the invitation email
        send_invitation_email(invitation_obj)

        return Response({'message': 'Invitation created successfully'}, status=status.HTTP_201_CREATED)

class AcceptClinicianInvitationView(generics.CreateAPIView):
    """
    Accepts an invitation to create an account for a clinician
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Accepts an invitation to create an account for a clinician
        """
        invitation_token = kwargs.get('invitation_token')
        invitation_obj = ClinicianInvitation.objects.get(
            record_id=invitation_token
        )


def send_invitation_email(invitation_obj):
    """
    Sends an invitation email to the clinician
    """
    # the following implementation is a mock implemntation that saves the invitation endpoint locally
    # for development and testing purposes. 
    # TODO: Implement a real email sending mechanism
    invitation_url = reverse('organizations:accept-invitation', kwargs={'invitation_token': invitation_obj.record_id})
    invitation_file_name = f'invitation_{invitation_obj.record_id}.txt'
    invitation_file_path = os.path.join('/app/invitations', invitation_file_name)
    # create the directory if it doesn't exist
    os.makedirs(os.path.dirname(invitation_file_path), exist_ok=True)
    with open(invitation_file_path, 'w') as f:
        f.write(invitation_url)
