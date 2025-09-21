from rest_framework import serializers
from .models import CareTeamMembership

class CareTeamMembershipSerializer(serializers.ModelSerializer):
    membership_id = serializers.UUIDField(source='record_id', read_only=True)
    class Meta:
        model = CareTeamMembership
        fields = ['membership_id', 'patient', 'clinician', 'role', 'status', 'managing_organization', 'assigned_at', 'assigned_by', 'reason_for_assignment']
        read_only_fields = ['patient', 'status', 'managing_organization', 'membership_id','assigned_at', 'assigned_by']