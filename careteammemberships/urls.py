from django.urls import path
from .views import PatientCareTeamMembershipCreateListView, CareTeamMembershipRetrieveDeactivateView

urlpatterns = [
    path('<uuid:organization_id>/patients/<uuid:patient_id>/careteam-memberships/', 
    PatientCareTeamMembershipCreateListView.as_view()),
    path('<uuid:organization_id>/careteam-memberships/<uuid:membership_id>/', 
    CareTeamMembershipRetrieveDeactivateView.as_view()),
    path('<uuid:organization_id>/careteam-memberships/<uuid:membership_id>/deactivate/', 
    CareTeamMembershipRetrieveDeactivateView.as_view())
]