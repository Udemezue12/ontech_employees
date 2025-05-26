import os
from django.conf import settings


def document(instance, filename):
    return os.path.join('documents', filename)


def image(instance, filename):
    return os.path.join('images', filename)