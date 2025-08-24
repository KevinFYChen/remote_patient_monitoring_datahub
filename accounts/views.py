from rest_framework import generics, permissions, mixins
from .serializers import RpmUserSerializer, RpmPatientSerializer, RpmClinicianSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import LoginAttempt, RpmUser, ClinicianProfile
from .serializers import LoginAttemptSerializer, ClinicianProfileSerializer
from .permissions import IsUserForClinicianProfile, IsClinician
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

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

class ClinicianProfileView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    serializer_class = ClinicianProfileSerializer
    permission_classes = [IsClinician]

    def get_object(self):
        return get_object_or_404(ClinicianProfile, user=self.request.user)
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'clinician_profile'):
            raise PermissionDenied("Clinician profile already exists.")
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        if not hasattr(self.request.user, 'clinician_profile'):
            raise PermissionDenied("Clinician profile does not exist.")
        serializer.save()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
