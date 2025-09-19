from rest_framework import serializers
from .models import Observation

class ObservationSerializer(serializers.ModelSerializer):
    observation_id = serializers.UUIDField(source='record_id', read_only=True)

    class Meta:
        model = Observation
        fields = [
            'observation_id',
            'patient',
            'loinc_code',
            'metric_display_name',
            'category',
            'value',
            'unit',
            'effective_timestamp',
            'device_id',
            'status',
            'notes',
        ]
        read_only_fields = ['patient']
    