from rest_framework import serializers
from .models import RpmUser, LoginAttempt
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
        extra_kwargs = {
            'role': {'read_only': True},
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
        }

class RpmPatientSerializer(RpmUserSerializer):
    def create(self, validated_data):
        return super().create(RoleChoices.PATIENT, validated_data)

class RpmClinicianSerializer(RpmUserSerializer):
    def create(self, validated_data):
        return super().create(RoleChoices.CLINICIAN, validated_data)

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
        