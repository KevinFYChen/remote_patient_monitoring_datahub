import os
from rest_framework import mixins
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework import generics, permissions, views, viewsets
from accounts.permissions import IsOrganizationAdminForOrg, IsPatient
from accounts.models import RpmUser
from .models import Organization, OrganizationInvitation, OrganizationMembership
from datetime import timedelta, datetime, timezone
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import RpmClinicianSerializer, ClinicianProfileSerializer
from .serializers import OrganizationInvitationSerializer, OrganizationSerializer, OrganizationMembershipSerializer, PatientOrganizationConsentSerializer
from django.db import transaction
from accounts.models import ClinicianProfile



class OrganizationViewSet(viewsets.ModelViewSet):
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
    List or Create an organization admin
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
                    'approved_by': request.user.organization_memberships.filter(
                        organization_id=organization.record_id,
                        status='active'
                    ).first(),
                    'approved_at': datetime.now(tz=timezone.utc)
                },
            )

            if not created and (membership.role != 'admin' or membership.status != 'active'):
                membership.role = 'admin'
                membership.status = 'active'
                membership.approved_at = datetime.now(tz=timezone.utc)
                membership.approved_by = request.user.organization_memberships.filter(
                    organization_id=organization.record_id,
                    status='active'
                ).first()
                membership.save(update_fields=['role', 'status', 'approved_at', 'approved_by'])

        data = self.serializer_class(membership).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class OrganizationInvitationListCreateView(generics.ListCreateAPIView):
    """
    Creates an invitation for a clinician to create an account in an organization
    """
    permission_classes = [IsOrganizationAdminForOrg]
    serializer_class = OrganizationInvitationSerializer
    queryset = OrganizationInvitation.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Create an invitation for a clinician to create an account in an organization
        """
        invitee_email = request.data.get('invitee_email')
        organization_id = kwargs.get('organization_id')
        # check if the invitation already exists
        if OrganizationInvitation.objects.filter(
            invitee_email=invitee_email,
            organization_id=organization_id,
            status='pending',
            expires_at__gt=datetime.now(tz=timezone.utc)
        ).exists():
            return Response({'error': 'Invitation already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the clinician already has an account
        if OrganizationMembership.objects.filter(
            user__email=invitee_email,
            organization_id=organization_id,
            status__in=['active', 'pending']
        ).exists():
            return Response({'error': 'Clinician already has an account'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Expiration time is 1 day from now, in UTC
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=1)

        invitation_obj = OrganizationInvitation(
            expires_at=expires_at,
            invitee_email=invitee_email,
            organization_id=organization_id,
            invited_by=request.user.organization_memberships.filter(
                organization_id=organization_id,
                status='active'
            ).first(),
            status='pending'
        )
        # validate the invitation object and save it
        invitation_obj.full_clean()
        invitation_obj.save()

        # send the invitation email
        send_invitation_email(invitation_obj)
        return Response({'message': 'Invitation created successfully'}, status=status.HTTP_201_CREATED)

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


class AcceptOrganizationInvitationView(views.APIView):
    """
    Accepts an invitation to create an account for a organization member
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Accepts an invitation to create an account for a clinician
        """
        invitation_token = kwargs.get('invitation_token')
        try:
            invitation_obj = OrganizationInvitation.objects.get(
                record_id=invitation_token,
                expires_at__gt=datetime.now(tz=timezone.utc),
                status="pending"
            )
        except OrganizationInvitation.DoesNotExist:
            return Response({'error': 'Active invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If user does not exists, create a new user
        invitee_user = RpmUser.objects.filter(email=invitation_obj.invitee_email).first()

        # If organization membership already exists, return a 400 error
        if invitee_user and OrganizationMembership.objects.filter(
            user=invitee_user,
            organization=invitation_obj.organization
        ).exists():
            return Response({'error': 'Clinician already has an account'}, status=status.HTTP_409_CONFLICT)

        with transaction.atomic():
            # If user does not exists, create a new user
            if not invitee_user:
                password = request.data.get('password')
                clinician_serializer = RpmClinicianSerializer(
                    data={
                        'email': invitation_obj.invitee_email,
                        'password': password
                    }
                )
                clinician_serializer.is_valid(raise_exception=True)
                invitee_user = clinician_serializer.save()
            
            # create a new organization membership
            org_membership_serializer = OrganizationMembershipSerializer(
                data={
                    "role": "member",
                    "status": "pending",
                }
                )
            org_membership_serializer.is_valid(raise_exception=True)
            org_membership_serializer.save(
                user=invitee_user,
                organization=invitation_obj.organization,
            )
            
            # update the invitation status
            invitation_obj.status = "accepted"
            invitation_obj.save()
        
        return Response(
            {
                'message': 'Registration successful, your account is pending approval',
                'user': RpmClinicianSerializer(invitee_user).data,
                'organization_membership': org_membership_serializer.data
            }, 
            status=status.HTTP_201_CREATED
        )

class ApproveClinicianMembershipView(views.APIView):
    """
    Verifies the organization membership and the clinician profile of a clinician
    If the clinician profile was already verified, or the membership is already approved,
    It will still return a 200 status code. Hence this endpoint is idempotent.
    """
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [IsOrganizationAdminForOrg]

    def post(self, request, organization_id, membership_id):
        membership = get_object_or_404(
            OrganizationMembership, 
            record_id=membership_id,
            organization_id=organization_id
            )
        user = membership.user

        if not hasattr(user, 'clinician_profile'):
            return Response({'error': 'Clinician profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.clinician_profile.credentials_verified:
            return Response({'error': 'Clinician profile is not verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        if membership.status != 'pending':
            return Response({'error': 'Clinician membership status is not pending'}, status=status.HTTP_400_BAD_REQUEST)


        with transaction.atomic():
            membership.status = 'active'
            membership.approved_at = datetime.now(tz=timezone.utc)
            membership.approved_by = request.user.organization_memberships.filter(
                organization_id=organization_id,
                status='active'
            ).first()
            membership.save(update_fields=['status', 'approved_at', 'approved_by'])
        
        return Response(
            {
                'message': 'Clinician membership approved',
                'organization_membership': self.serializer_class(membership).data
            }, 
            status=status.HTTP_200_OK
            )

class UpdateRetrieveListOrganizationMembersViewset(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Viewset to update, retrieve, and list organization members
    """
    permission_classes = [permissions.IsAdminUser | IsOrganizationAdminForOrg]
    serializer_class = OrganizationMembershipSerializer
    
    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            organization_id=self.kwargs['organization_id'],
            status__in=['active', 'pending'],
        )
    
    def get_object(self):
        return get_object_or_404(OrganizationMembership, record_id=self.kwargs['membership_id'])
        
class ListOrganizationClinicianProfilesView(generics.ListAPIView):
    """
    View class to list clinician profiles for an organization
    """
    permission_classes = [permissions.IsAdminUser | IsOrganizationAdminForOrg]
    serializer_class = ClinicianProfileSerializer

    def get_queryset(self):
        return ClinicianProfile.objects.filter(
            user__organization_membership__organization_id=self.kwargs['organization_id']
        ).distinct()

class CreatePatientOrganizationConsentView(generics.CreateAPIView):
    """
    Creates a patient organization consent. This gives the organization permission to access the patient's data.
    """
    permission_classes = [IsPatient]
    serializer_class = PatientOrganizationConsentSerializer

    def perform_create(self, serializer):
        # Ensure that user is a patient
        if not self.request.user.patient:
            return Response({'error': f'Patient profile not found for user {request.user}'}, status=status.HTTP_404_NOT_FOUND)
        # Ensure organization exists
        organization = get_object_or_404(Organization, record_id=self.kwargs.get('organization_id'))
        serializer.save(
            patient=self.request.user.patient, 
            organization=organization)
