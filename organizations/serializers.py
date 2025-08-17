from rest_framework import serializers
from .models import ClinicianInvitation

class ClinicianInvitationSerializer(serializers.ModelSerializer):
    clinician_email = serializers.EmailField()
    class Meta:
        model = ClinicianInvitation
        fields = ['clinician_email', 'organization_id', 'invited_by', 'status', 'expires_at']

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['record_id', 'name', 'address', 'contact_number', 'description', 'organization_type', 'active']
