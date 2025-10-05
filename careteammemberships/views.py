from django.shortcuts import render
from accounts.permissions import IsOrganizationAdminForOrg
from organizations.models import Organization
from .models import CareTeamMembership
from rest_framework import mixins, generics
from .serializers import CareTeamMembershipSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsClinicianForPatient
from patients.models import Patient
from organizations.models import PatientOrganizationConsent

class CareTeamMembershipCreateListView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    serializer_class = CareTeamMembershipSerializer
    permission_classes = [IsClinicianForPatient | IsOrganizationAdminForOrg]


    def get_queryset(self):
        return CareTeamMembership.objects.filter(
            managing_organization_id=self.kwargs['organization_id'],
            patient_id=self.kwargs['patient_id']
        )
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Creates a care team membership for a clinician given a patient
        """
        # Check if patient had given consent to the organization
        if not PatientOrganizationConsent.objects.filter(
            patient_id=self.kwargs['patient_id'],
            organization_id=self.kwargs['organization_id'],
            is_revoked=False
        ).exists():
            return Response({'error': 'Patient has not given consent to the organization'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        # if reason for assignment is not provided, set it to an empty string
        if 'reason_for_assignment' not in data:
            data['reason_for_assignment'] = ''
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        managing_organization = get_object_or_404(
            Organization,
            record_id=self.kwargs['organization_id']
        )
        patient = get_object_or_404(
            Patient,
            record_id=self.kwargs['patient_id']
        )
        serializer.save(
            status='active',
            assigned_by=self.request.user.organization_memberships.filter(
                organization_id=self.kwargs['organization_id'],
                status='active'
            ).first(),
            managing_organization=managing_organization,
            patient=patient
        )

class CareTeamMembershipRetrieveView(
    generics.RetrieveAPIView
):
    """
    View to retrieve a care team membership
    """
    serializer_class = CareTeamMembershipSerializer
    permission_classes = [IsOrganizationAdminForOrg | IsClinicianForPatient]
    
    def get_object(self):
        return get_object_or_404(
            CareTeamMembership, 
            record_id=self.kwargs['membership_id'],
            managing_organization_id=self.kwargs['organization_id']
            )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class CareTeamMembershipDeactivateView(
    generics.GenericAPIView,
):
    serializer_class = CareTeamMembershipSerializer
    permission_classes = [IsOrganizationAdminForOrg]

    def post(self, request, *args, **kwargs):
        """
        Deactivates a care team membership
        """
        membership = get_object_or_404(
            CareTeamMembership, 
            record_id=self.kwargs['membership_id'],
            managing_organization_id=self.kwargs['organization_id']
            )
        membership.status = 'inactive'
        membership.save()
        return Response(status=status.HTTP_200_OK)
