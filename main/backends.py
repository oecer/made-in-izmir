from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOrUsernameBackend(ModelBackend):
    """
    Authentication backend that allows users to log in with either their
    username or their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # First try to find the user by username (exact match)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Fall back to email lookup (case-insensitive)
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                # Run the default password hasher to mitigate timing attacks
                User().set_password(password)
                return None
            except User.MultipleObjectsReturned:
                # If multiple accounts share the same email, deny login
                return None

        # Check the password and that the user is allowed to authenticate
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
