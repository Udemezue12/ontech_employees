"""
ASGI config for payroll_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

env = os.getenv('DJANGO_ENV', 'dev')  # Defaults to 'dev' if not set

if env == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_system.production_settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_system.settings')

application = get_asgi_application()
