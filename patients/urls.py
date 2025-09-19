from django.urls import path
from . import views
from django.urls import include


urlpatterns = [
    path('', views.CreateUpdateRetrievePatientViewSet.as_view(
        {'post': 'create'}
    ), name='create-patient'),
    path('me/', views.CreateUpdateRetrievePatientViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}
    ), name='retrieve-update-patient'),
]
