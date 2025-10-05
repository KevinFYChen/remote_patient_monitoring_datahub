from django.urls import path
from . import views

urlpatterns = [
    path('', views.PatientObservationViewSet.as_view(
        {'get': 'list', 'post': 'create'}
    ), name='patient-observations-list-create'),
    path('<uuid:observation_id>/', views.PatientObservationViewSet.as_view(
        {'get': 'retrieve'}
    ), name='patient-observation-retrieve'),
]