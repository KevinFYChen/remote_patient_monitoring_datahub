from rest_framework import serializers
from .models import RpmUser, LoginAttempt


class RpmUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = RpmUser.objects.create_user(**validated_data)
        return user
    
    class Meta:
        model = RpmUser
        fields = ['email', 'is_active', 'is_staff', 'password','role']

class LoginAttemptSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email')
    class Meta:
        model = LoginAttempt
        fields = ['user_email', 'success','timestamp','ip_address', 'user_agent']
        read_only_fields = fields
        