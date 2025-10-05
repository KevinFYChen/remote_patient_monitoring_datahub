from django.urls import path
from .views import CareTeamMembershipCreateListView, CareTeamMembershipRetrieveView, CareTeamMembershipDeactivateView

urlpatterns = [
    path('<uuid:organization_id>/patients/<uuid:patient_id>/careteam-memberships/', 
    CareTeamMembershipCreateListView.as_view()),
    path('<uuid:organization_id>/patients/<uuid:patient_id>/careteam-memberships/<uuid:membership_id>/', 
    CareTeamMembershipRetrieveView.as_view()),
    path('<uuid:organization_id>/patients/<uuid:patient_id>/careteam-memberships/<uuid:membership_id>/deactivate/', 
    CareTeamMembershipDeactivateView.as_view())
]