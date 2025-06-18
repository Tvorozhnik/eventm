from django.contrib.auth import backends
from django.conf import settings

class RoleBasedAuthBackend(backends.ModelBackend):
    def get_user_role_redirect(self, user):
        return settings.LOGIN_REDIRECT_URL.get(user.role, '/')

    def authenticate(self, request, **kwargs):
        user = super().authenticate(request, **kwargs)
        if user:
            request.session['user_role'] = user.role
        return user