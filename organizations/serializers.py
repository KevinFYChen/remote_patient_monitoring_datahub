from rest_framework import serializers
from .models import OrganizationInvitation, Organization, OrganizationMembership, PatientOrganizationConsent

class OrganizationInvitationSerializer(serializers.ModelSerializer):
    invitee_email = serializers.EmailField()
    class Meta:
        model = OrganizationInvitation
        fields = ['invitee_email', 'organization', 'invited_by', 'status', 'expires_at']

class OrganizationSerializer(serializers.ModelSerializer):
    organization_id = serializers.UUIDField(source='record_id', read_only=True)
    class Meta:
        model = Organization
        fields = ['organization_id', 'name', 'address', 'contact_number', 'description', 'organization_type', 'active']
        read_only_fields = ['active']

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    membership_id = serializers.UUIDField(source='record_id', read_only=True)
    class Meta:
        model = OrganizationMembership
        fields = ['membership_id', 'user', 'organization', 'role', 'status', 'approved_at', 'approved_by']


class PatientOrganizationConsentSerializer(serializers.ModelSerializer):
    consent_id = serializers.UUIDField(source='record_id', read_only=True)

    class Meta:
        model = PatientOrganizationConsent
        fields = ['consent_id', 'patient', 'organization', 'consented_at', 'expires_at', 'is_revoked', 'revoked_at']
        read_only_fields = ['patient', 'organization']
