from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('token/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='refresh'),
    path('token/verify/', views.VerifyTokenView.as_view(), name='verify'),
    path('me/', views.MeView.as_view(), name='me'),
    path('login-attempts/', views.LoginAttemptsListView.as_view(), name='login-attempts'),
]