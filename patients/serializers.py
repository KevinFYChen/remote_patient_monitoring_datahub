from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    patient_id = serializers.UUIDField(source='record_id', read_only=True)

    class Meta:
        model = Patient
        fields = ['patient_id', 'user', 'first_name', 'last_name', 'date_of_birth', 'gender', 'contact_number', 'address']
        read_only_fields = ['user']