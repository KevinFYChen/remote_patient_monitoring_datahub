from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.ListRpmUsersView.as_view(), name='list-rpm-users'),
    path('register/patient/', views.CreatePatientView.as_view(), name='register-patient'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('login-attempts/', views.LoginAttemptsListView.as_view(), name='login-attempts'),
    path('clinician-profile/', views.CreateRetrieveClinicianProfileView.as_view(), name='create-retrieve-clinician-profile'),
    path('clinician-profile/<uuid:clinician_profile_id>/', views.UpdateClinicianProfileView.as_view(), name='update-clinician-profile'),
    path('clinician-profile/<uuid:clinician_profile_id>/verify/', views.VerifyClinicianProfileView.as_view(), name='verify-clinician-profile'),
]