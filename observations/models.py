from django.db import models
from common.models import TimeStampedModel
from patients.models import Patient
import uuid

class ObservationStatus(models.TextChoices):
    FINAL = "final", "Final"
    AMENDED = "amended", "Amended"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"
    PRELIMINARY = "preliminary", "Preliminary"
    CANCELLED = "cancelled", "Cancelled"

class ObservationCategory(models.TextChoices):
    VITAL_SIGNS = "vital-signs", "Vital signs"
    LABORATORY = "laboratory", "Laboratory"
    SURVEY = "survey", "Survey"
    PROCEDURE = "procedure", "Procedure"
    IMAGING = "imaging", "Imaging"
    EXAM = "exam", "Exam"
    THERAPY = "therapy", "Therapy"
    ACTIVITY = "activity", "Activity"
    SOCIAL_HISTORY = "social-history", "Social history"

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
    loinc_code = models.CharField(max_length=20, help_text="LOINC code for the metric")
    metric_display_name = models.CharField(blank=True, null=True, max_length=255, help_text="Display of the metric")
    category = models.CharField(max_length=255, help_text="Category of the metric", choices=ObservationCategory.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, help_text="Unit of the metric")
    effective_timestamp = models.DateTimeField(help_text="timestamp of when the observation was made")
    device_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID of the device that made the observation")
    status = models.CharField(max_length=20, choices=ObservationStatus.choices)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'observation'
