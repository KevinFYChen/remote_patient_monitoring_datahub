from uuid import UUID
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework import generics, permissions
from accounts.permissions import IsOrganizationAdminForOrg
from accounts.models import RpmUser
from .models import Organization, ClinicianInvitation, OrganizationMembership
from datetime import timedelta, datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import RpmClinicianSerializer
from .serializers import ClinicianInvitationSerializer, OrganizationSerializer, OrganizationMembershipSerializer
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
import os


class OrganizationViewSet(ModelViewSet):
    """
    Viewset for the Organization model
    """
    lookup_field = 'record_id'
    lookup_url_kwarg = 'organization_id'
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'destroy']:
            return [permissions.IsAdminUser()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [(permissions.IsAdminUser | IsOrganizationAdminForOrg)()]
        return super().get_permissions()

class ListCreateOrganizationAdminView(generics.ListCreateAPIView):
    """
    Creates an organization admin
    """
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAdminUser | IsOrganizationAdminForOrg]

    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            organization_id=self.kwargs['organization_id'],
            role='admin'
        )

    def post(self, request, *args, **kwargs):
        """
        Creates an organiation admin
        """
        user_serializer = RpmClinicianSerializer(data=request.data, context={'request': request})
        user_serializer.is_valid(raise_exception=True)

        organization = get_object_or_404(Organization, record_id=kwargs['organization_id'])

        with transaction.atomic():
            email = user_serializer.validated_data['email']
            user = RpmUser.objects.filter(email=email).first()
            if not user:
                user = user_serializer.save()

            membership, created = OrganizationMembership.objects.get_or_create(
                user=user,
                organization=organization,
                defaults={
                    'role': 'admin',
                    'status': 'active',
                    'approved_at': datetime.now(tz=timezone.utc),
                    'approved_by': request.user,
                },
            )

            if not created and (membership.role != 'admin' or membership.status != 'active'):
                membership.role = 'admin'
                membership.status = 'active'
                membership.approved_at = datetime.now(tz=timezone.utc)
                membership.approved_by = request.user
                membership.save(update_fields=['role', 'status', 'approved_at', 'approved_by'])

        data = self.serializer_class(membership).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class SendClinicianInvitationView(generics.ListCreateAPIView):
    """
    Creates an invitation for a clinician to create an account in an organization
    """
    permission_classes = [IsOrganizationAdminForOrg]
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
