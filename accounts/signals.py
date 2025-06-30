from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from .models import LoginAttempt

@receiver(user_logged_in)
def audit_success(sender, request, user, **kw):
    LoginAttempt.objects.create(
        user=user,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        success=True
    )

@receiver(user_login_failed)
def audit_fail(sender, credentials, request, **kw):
    LoginAttempt.objects.create(
        user=None,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        success=False,
    )