from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import RpmUserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .models import LoginAttempt
from .serializers import LoginAttemptSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = RpmUserSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(TokenObtainPairView):
    pass

class RefreshTokenView(TokenRefreshView):
    pass

class VerifyTokenView(TokenVerifyView):
    pass

class MeView(generics.RetrieveAPIView):
    serializer_class = RpmUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LoginAttemptsListView(generics.ListAPIView):
    serializer_class = LoginAttemptSerializer
    permission_classes = [permissions.IsAuthenticated & permissions.IsAdminUser]

    def get_queryset(self):
        return LoginAttempt.objects.all()


