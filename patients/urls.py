from django.urls import path
from . import views
from django.urls import include
from observations.views import ClinicianObservationViewSet



urlpatterns = [
    path('', views.CreateUpdateRetrievePatientViewSet.as_view(
        {'post': 'create'}
    ), name='create-patient'),
    path('me/', views.CreateUpdateRetrievePatientViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}
    ), name='retrieve-update-patient'),
    path('<uuid:patient_id>/observations/', ClinicianObservationViewSet.as_view(
        {'get': 'list'}
    ), name='clinician-observations-list'),
    path('<uuid:patient_id>/observations/<uuid:observation_id>/', ClinicianObservationViewSet.as_view(
        {'get': 'retrieve'}
    ), name='clinician-observation-retrieve'),
]
