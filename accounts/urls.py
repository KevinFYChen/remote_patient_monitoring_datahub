from django.urls import path
from . import views

urlpatterns = [
    path('register/patient/', views.CreatePatientView.as_view(), name='register-patient'),
    path('register/clinician/', views.CreateClinicianView.as_view(), name='register-clinician'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('login-attempts/', views.LoginAttemptsListView.as_view(), name='login-attempts'),
    path('clinician-profile/', views.ClinicianProfileView.as_view(), name='clinician-profile'),
]