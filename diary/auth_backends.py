# diary/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """email と password で認証"""
    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        login_id = (email or username or "").strip()
        if not login_id or not password:
            return None
        try:
            user = UserModel.objects.get(email__iexact=login_id)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
