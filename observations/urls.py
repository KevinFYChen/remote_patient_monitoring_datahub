from django.urls import path
from . import views

urlpatterns = [
    path('patient/', views.PatientObservationViewSet.as_view(
        {'get': 'list', 'post': 'create'}
    ), name='patient-observations-list-create'),
    path('patient/<uuid:observation_id>/', views.PatientObservationViewSet.as_view(
        {'get': 'retrieve'}
    ), name='patient-observation-retrieve'),
    path('clinician/<uuid:patient_id>/', views.ClinicianObservationViewSet.as_view(
        {'get': 'list'}
    ), name='clinician-observations-list'),
    path('clinician/<uuid:patient_id>/<uuid:observation_id>/', views.ClinicianObservationViewSet.as_view(
        {'get': 'retrieve'}
    ), name='clinician-observation-retrieve'),
]