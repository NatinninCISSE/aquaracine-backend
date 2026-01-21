"""
Custom authentication backends for Aqua-Racine.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """
    Authenticate using email address instead of username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 'username' field contains the email in our login form
        email = username
        if email is None:
            email = kwargs.get('email')

        if email is None or password is None:
            return None

        try:
            # Try to find user by email
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Try username as fallback
            try:
                user = User.objects.get(username__iexact=email)
            except User.DoesNotExist:
                # Run the default password hasher once to reduce timing attacks
                User().set_password(password)
                return None
        except User.MultipleObjectsReturned:
            # If multiple users have the same email, get the first active one
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user is None:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
