from django.db import models
from common.models import TimeStampedModel
from patients.models import Patient
import uuid

class Device(TimeStampedModel):
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    manufacturer = models.CharField(max_length=80)
    model_number = models.CharField(max_length=40)
    serial_number = models.CharField(max_length=40, db_index=True)
    udi_carrier = models.CharField(max_length=200, blank=True)  # GS1/UDI-DI+PI
    firmware = models.CharField(max_length=40, blank=True)
    device_type = models.CharField(max_length=120)              # LOINC / GMDN / SNOMED code
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)    

    class Meta:
        db_table = 'device'

class Observation(TimeStampedModel):
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    metric_code = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    effective_timestamp = models.DateTimeField() # timestamp of when the observation was made
    device_id = models.CharField(max_length=255, blank=True, null=True)
    raw_fhir_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'observation'
