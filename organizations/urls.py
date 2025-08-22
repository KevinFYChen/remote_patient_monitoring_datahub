from django.urls import path
from . import views 
from rest_framework.routers import DefaultRouter
from django.urls import include

router = DefaultRouter()
router.register('', views.OrganizationViewSet, basename='organization')

app_name = 'organizations'
urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:organization_id>/invitations/', views.SendClinicianInvitationView.as_view(), name='send-invitation'),
    path('invitations/<uuid:invitation_token>/accept/', views.AcceptClinicianInvitationView.as_view(), name='accept-invitation'),
    path('<uuid:organization_id>/admins/', views.ListCreateOrganizationAdminView.as_view(), name='list-create-organization-admin'),
]