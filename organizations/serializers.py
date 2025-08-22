from rest_framework import serializers
from .models import ClinicianInvitation, Organization, OrganizationMembership

class ClinicianInvitationSerializer(serializers.ModelSerializer):
    clinician_email = serializers.EmailField()
    class Meta:
        model = ClinicianInvitation
        fields = ['clinician_email', 'organization', 'invited_by', 'status', 'expires_at']

class OrganizationSerializer(serializers.ModelSerializer):
    organization_id = serializers.UUIDField(source='record_id', read_only=True)
    class Meta:
        model = Organization
        fields = ['organization_id', 'name', 'address', 'contact_number', 'description', 'organization_type', 'active']

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMembership
        fields = ['user', 'organization', 'role', 'status', 'approved_at', 'approved_by']
