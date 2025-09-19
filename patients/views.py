from django.shortcuts import render
from .models import Patient
from rest_framework import permissions, viewsets, mixins
from django.shortcuts import get_object_or_404
from .serializers import PatientSerializer


class CreateUpdateRetrievePatientViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Patient, user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

