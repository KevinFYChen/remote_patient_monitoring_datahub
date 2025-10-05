from rest_framework import generics, permissions, mixins
from .serializers import RpmUserSerializer, RpmPatientSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import LoginAttempt, RpmUser, ClinicianProfile
from .serializers import LoginAttemptSerializer, ClinicianProfileSerializer
from .permissions import IsClinician, IsOrganizationAdmin, IsOrganizationAdminForOrg
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets
from django.db import transaction
from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status

class ListRpmUsersView(generics.ListAPIView):
    serializer_class = RpmUserSerializer
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]
    queryset = RpmUser.objects.all()

class CreatePatientUserView(generics.CreateAPIView):
    serializer_class = RpmPatientSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logged_in_user = RpmUser.objects.get(email=request.data.get("email"))
            LoginAttempt.objects.create(
                user=logged_in_user,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                success=True
            )
        else:
            LoginAttempt.objects.create(
                user=None,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                success=False
            )
        return response

class RefreshTokenView(TokenRefreshView):
    pass

class MeView(generics.RetrieveAPIView):
    serializer_class = RpmUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LoginAttemptsListView(generics.ListAPIView):
    serializer_class = LoginAttemptSerializer
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]

    def get_queryset(self):
        return LoginAttempt.objects.all()

class CreateRetrieveClinicianProfileView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView
):
    """
    Viewset to create or retrieve the clinician profile for the current user
    """
    serializer_class = ClinicianProfileSerializer
    permission_classes = [IsClinician | IsOrganizationAdmin]

    def get_object(self):
        return get_object_or_404(ClinicianProfile, user=self.request.user)
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'clinician_profile'):
            raise PermissionDenied("Clinician profile already exists.")
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class UpdateClinicianProfileView(generics.UpdateAPIView):
    """
    Viewset to update the clinician profile. This is restricted to admin users or organization admins.
    """
    serializer_class = ClinicianProfileSerializer
    permission_classes = [permissions.IsAdminUser | IsOrganizationAdmin]

    def get_object(self):
        clinician_profile_id = self.kwargs['clinician_profile_id']
        if not self.request.user.is_staff:
            # if not platform admin, check that user is the organization admin at one of the organizations that the clinician is a member of
            is_organization_admin = verify_user_is_admin_for_clinician(self.request.user, clinician_profile_id)
            if not is_organization_admin:
                raise PermissionDenied("You are not authorized to update this clinician profile.")
        return get_object_or_404(ClinicianProfile, record_id=clinician_profile_id)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class VerifyClinicianProfileView(views.APIView):
    """
    Viewset to verify the clinician profile. This is restricted to admin users or organization admins.
    """
    serializer_class = ClinicianProfileSerializer
    permission_classes = [permissions.IsAdminUser | IsOrganizationAdmin]

    def post(self, request, clinician_profile_id, *args, **kwargs):
        clinician_profile = get_object_or_404(ClinicianProfile, record_id=clinician_profile_id)
        if not self.request.user.is_staff:
            # if not platform admin, check that user is the organization admin at one of the organizations that the clinician is a member of
            is_organization_admin = verify_user_is_admin_for_clinician(self.request.user, clinician_profile_id)
            if not is_organization_admin:
                raise PermissionDenied("You are not authorized to verify this clinician profile.")
        with transaction.atomic():
            clinician_profile.credentials_verified = True
            clinician_profile.verification_datetime = datetime.now(tz=timezone.utc)
            clinician_profile.verified_by = request.user
            clinician_profile.save(update_fields=['credentials_verified', 'verification_datetime', 'verified_by'])
        return Response(
            {
                'message': 'Clinician profile verified', 
                'clinician_profile': self.serializer_class(clinician_profile).data
            }, status=status.HTTP_200_OK)

def verify_user_is_admin_for_clinician(request_user, clinician_profile_id):
    clinician_profile = get_object_or_404(ClinicianProfile, record_id=clinician_profile_id)
    clinician_user = clinician_profile.user
    request_user_organization_ids = request_user.organization_memberships.filter(
        status='active',
        role='admin'
        ).values_list('organization_id', flat=True)
    is_organization_admin = clinician_user.organization_memberships.filter(
        status__in=['active', 'pending'],
        organization_id__in=request_user_organization_ids
    ).exists()
    return is_organization_admin

