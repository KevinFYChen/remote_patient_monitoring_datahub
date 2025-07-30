from rest_framework import generics, permissions
from .serializers import RpmUserSerializer, RpmPatientSerializer, RpmClinicianSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import LoginAttempt
from .serializers import LoginAttemptSerializer

class CreatePatientView(generics.CreateAPIView):
    serializer_class = RpmPatientSerializer
    permission_classes = [permissions.AllowAny]

class CreateClinicianView(generics.CreateAPIView):
    serializer_class = RpmClinicianSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(TokenObtainPairView):
    pass

class RefreshTokenView(TokenRefreshView):
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


