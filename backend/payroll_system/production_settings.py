from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

dotenv_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), '..', '.env')
load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'knox',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_rest_passwordreset',
    'widget_tweaks',
    'django.contrib.humanize',
    'employees.apps.EmployeesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'employees.middleware.NoCacheMiddleware',
]

ROOT_URLCONF = 'payroll_system.urls'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
    "X-CSRFToken"
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'knox.auth.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

REST_KNOX = {
    'TOKEN_TTL': timedelta(minutes=30),
    'AUTO_REFRESH': False,
    'USER_SERIALIZER': 'employees.serializers.LoginSerializer',
}

# Cookie and CSRF settings for production
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False

CSRF_COOKIE_NAME = 'csrftoken'

# Templates and Static
REACT_BUILD_DIR = os.path.join(BASE_DIR, 'frontend', 'build')
DJANGO_TEMPLATES_DIR = os.path.join(BASE_DIR, 'backend', 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [DJANGO_TEMPLATES_DIR, REACT_BUILD_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'employees.context_processors.notification_count',
            ],
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(REACT_BUILD_DIR, 'static'),
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WSGI_APPLICATION = 'payroll_system.wsgi.application'
AUTH_USER_MODEL = 'employees.CustomUser'

AUTHENTICATION_BACKENDS = [
    'employees.auth_backend.Email_Backend',
    'django.contrib.auth.backends.ModelBackend'
]



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'pay.db',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

WEBAUTHN_RP_ID = "ontech-systems.onrender.com"
WEBAUTHN_ALLOWED_ORIGINS = [
    "https://ontech-systems.onrender.com",
    "https://www.ontech-systems.onrender.com",
]

ALLOWED_HOSTS = [
    "ontech-systems.onrender.com",
    "www.ontech-systems.onrender.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://ontech-systems.onrender.com",
    "https://www.ontech-systems.onrender.com",
    "localhost",
    "127.0.0.1"
]

CSRF_TRUSTED_ORIGINS = [
    "https://ontech-systems.onrender.com",
    "https://www.ontech-systems.onrender.com",
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',  # You can change this to 'INFO' or 'WARNING' in production
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # Adjust based on environment
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

