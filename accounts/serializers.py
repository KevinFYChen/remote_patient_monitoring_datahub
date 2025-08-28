from rest_framework import serializers
from .models import RpmUser, LoginAttempt, ClinicianProfile
from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import RoleChoices

class RpmUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, role, validated_data):
        validated_data['role'] = role
        validated_data['is_active'] = True
        validated_data['is_staff'] = False
        user = RpmUser.objects.create_user(**validated_data)
        user.groups.add(Group.objects.get(name=user.get_role_display()))
        return user
    
    class Meta:
        model = RpmUser
        fields = ['email', 'is_active', 'is_staff', 'password','role']
        read_only_fields = ['role', 'is_active', 'is_staff']

class RpmPatientSerializer(RpmUserSerializer):
    def create(self, validated_data):
        return super().create("patient", validated_data)

class RpmClinicianSerializer(RpmUserSerializer):
    def create(self, validated_data):
        return super().create("clinician", validated_data)

class ClinicianProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClinicianProfile
        fields = [
            "user", 'first_name', 'last_name', 'npi_number', 'medical_license_number', 'license_state', 
            'license_expiration_date', 'specialty', 'credentials_verified', 'verification_date', 
            'verified_by']
        read_only_fields = ["user","credentials_verified",'verification_date', 'verified_by']

class RpmAnalystSerializer(RpmUserSerializer):
    def create(self, validated_data):
        return super().create(RoleChoices.ANALYST, validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

class LoginAttemptSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email')
    class Meta:
        model = LoginAttempt
        fields = ['user_email', 'success','timestamp','ip_address', 'user_agent']
        read_only_fields = fields
        