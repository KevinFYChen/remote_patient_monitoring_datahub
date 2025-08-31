from django.urls import path
from . import views 
from rest_framework.routers import DefaultRouter
from django.urls import include

router = DefaultRouter()
router.register('', views.OrganizationViewSet, basename='organization')

app_name = 'organizations'
urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:organization_id>/invitations/', views.OrganizationInvitationListCreateView.as_view(), name='invitation-list-create'),
    path('invitations/<uuid:invitation_token>/accept/', views.AcceptOrganizationInvitationView.as_view(), name='accept-invitation'),
    path('<uuid:organization_id>/admins/', views.ListCreateOrganizationAdminView.as_view(), name='list-create-organization-admin'),
    path('<uuid:organization_id>/clinician-profiles/', views.ListOrganizationClinicianProfilesView.as_view(), name='list-clinician-profiles'),
    path('<uuid:organization_id>/members/', views.UpdateRetrieveListOrganizationMembersViewset.as_view(
        {'get': 'list'}
    ), name='organization-members-list'),
    path('<uuid:organization_id>/members/<uuid:membership_id>/', views.UpdateRetrieveListOrganizationMembersViewset.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}
    ), name='organization-members-retrieve-update'),
    path('<uuid:organization_id>/members/<uuid:membership_id>/approve/', views.ApproveClinicianMembershipView.as_view(), name='approve-clinician-membership'),
]