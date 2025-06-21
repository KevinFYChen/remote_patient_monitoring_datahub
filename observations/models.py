from common.models import TimeStampedModel
from patients.models import Patient

class Observation(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    metric_code = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    effective_timestamp = models.DateTimeField() # timestamp of when the observation was made
    device_id = models.CharField(max_length=255, blank=True, null=True)
    raw_fhir_json = models.JSONField(blank=True, null=True)

