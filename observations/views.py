from rest_framework import mixins, permissions, viewsets
from .serializers import ObservationSerializer
from .models import Observation
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from patients.models import Patient
from rest_framework.exceptions import NotFound
from accounts.permissions import IsClinicianForPatient, IsPatient


class PatientObservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ObservationSerializer
    permission_classes = [IsPatient]

    def get_queryset(self):
        return Observation.objects.filter(
            patient_id=self.request.user.patient.record_id
        )

    def get_object(self):
        return get_object_or_404(
            Observation, 
            record_id=self.kwargs['observation_id'], 
            patient_id=self.request.user.patient.record_id
            )
    
    def perform_create(self, serializer):
        patient = getattr(self.request.user, 'patient', None)
        if not patient:
            raise NotFound("Patient not found")
        serializer.save(patient=patient)

class ClinicianObservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ObservationSerializer
    permission_classes = [IsClinicianForPatient]

    def get_queryset(self):
        return Observation.objects.filter(
            patient_id=self.kwargs['patient_id']
        )

    def get_object(self):
        return get_object_or_404(
            Observation, record_id=self.kwargs['observation_id'], patient_id=self.kwargs['patient_id'])
    