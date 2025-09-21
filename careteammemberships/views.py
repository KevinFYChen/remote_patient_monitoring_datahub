from django.shortcuts import render
from accounts.permissions import IsOrganizationAdminForOrg
from .models import CareTeamMembership
from rest_framework import mixins, generics
from .serializers import CareTeamMembershipSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

class PatientCareTeamMembershipCreateListView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    serializer_class = CareTeamMembershipSerializer
    permission_classes = [IsOrganizationAdminForOrg]

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
        serializer.save(
            patient=self.kwargs['patient_id'],
            status='active',
            managing_organization=self.kwargs['organization_id'],
            assigned_by=self.request.user
        )

class CareTeamMembershipRetrieveDeactivateView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
):
    """
    View to retrieve a care team membership
    """
    serializer_class = CareTeamMembershipSerializer
    permission_classes = [IsOrganizationAdminForOrg]
    
    def get_object(self):
        return get_object_or_404(
            CareTeamMembership, 
            record_id=self.kwargs['membership_id'],
            managing_organization_id=self.kwargs['organization_id']
            )



    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
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

