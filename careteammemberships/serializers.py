from rest_framework import serializers
from .models import CareTeamMembership
from accounts.models import ClinicianProfile
from organizations.models import Organization
from patients.models import Patient

class CareTeamMembershipSerializer(serializers.ModelSerializer):
    membership_id = serializers.UUIDField(source='record_id', read_only=True)
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    clinician = serializers.PrimaryKeyRelatedField(queryset=ClinicianProfile.objects.all())
    managing_organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CareTeamMembership
        fields = ['membership_id', 'patient', 'clinician', 'role', 'status', 'managing_organization', 'assigned_at', 'assigned_by', 'reason_for_assignment']
        read_only_fields = ['membership_id', 'status','assigned_at', 'assigned_by']