from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from common.models import TimeStampedModel

class RoleChoices(models.TextChoices):
        ADMIN = "admin", "Admin"
        CLINICIAN = "clinician", "Clinician"
        PATIENT = "patient", "Patient"

class RpmUserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if extra_fields.get('role') not in [role[0] for role in RoleChoices.choices]:
            raise ValueError(f"Invalid role: {extra_fields.get('role')}")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleChoices.ADMIN)
        return self.create_user(email, password, **extra_fields)

class RpmUser(AbstractBaseUser, PermissionsMixin):

    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=255, choices=RoleChoices.choices)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = RpmUserManager()

    class Meta:
        db_table = "account_user"

    def __str__(self) -> str: 
        return self.email
    

class ClinicianProfile(TimeStampedModel):
    """
    Profile for a clinician
    """
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        RpmUser, 
        on_delete=models.CASCADE,
        related_name='clinician_profile'
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    npi_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    medical_license_number = models.CharField(max_length=255)
    license_state = models.CharField(max_length=255)
    license_expiration_date = models.DateField()
    specialty = models.CharField(max_length=255)
    credentials_verified = models.BooleanField(default=False)
    verification_date = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(
        RpmUser, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='verified_clinician_profiles',
        related_query_name='verified_clinician_profile'
    )

    class Meta:
        db_table = "clinician_profile"


class LoginAttempt(models.Model):
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(RpmUser, on_delete=models.CASCADE)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    class Meta:
        db_table = "login_attempt"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} @ {self.timestamp} - {self.success}"
