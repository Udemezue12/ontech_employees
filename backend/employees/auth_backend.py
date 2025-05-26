from django.contrib.auth import get_user_model


User = get_user_model()


class Email_Backend:
    def authenicate(self, request, email=None, password=None):
        try:
            user = user.objects.get(email=email)
            if user.check_password(password):
                return user
        except:
            User.DoesNotExist:
        return None
from django.utils import timezone
from .models import ManualAttendance
from django.contrib.auth import get_user_model



    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
