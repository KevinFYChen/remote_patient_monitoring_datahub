from rest_framework import generics, permissions
from .serializers import RpmUserSerializer, RpmPatientSerializer, RpmClinicianSerializer, RpmAnalystSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import LoginAttempt, RpmUser
from .serializers import LoginAttemptSerializer

class CreatePatientView(generics.CreateAPIView):
    serializer_class = RpmPatientSerializer
    permission_classes = [permissions.AllowAny]

class CreateClinicianView(generics.CreateAPIView):
    serializer_class = RpmClinicianSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logged_in_user = RpmUser.objects.get(email=request.data.get("email"))
            LoginAttempt.objects.create(
                user=logged_in_user,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                success=True
            )
        else:
            LoginAttempt.objects.create(
                user=None,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                success=False
            )
        return response

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
