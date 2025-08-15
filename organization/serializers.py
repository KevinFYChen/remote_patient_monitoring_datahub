from rest_framework import serializers
from organization.models import ClinicianInvitation

class ClinicianInvitationSerializer(serializers.ModelSerializer):
    clinician_email = serializers.EmailField()
    class Meta:
        model = ClinicianInvitation
        fields = ['clinician_email']
