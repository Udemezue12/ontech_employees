from .models import Notification


def create_notification(user, message):
    Notification.objects.create(recipient=user, message=message)