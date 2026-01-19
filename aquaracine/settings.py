"""
Django settings for Aqua-Racine project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-aquaracine-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,.pythonanywhere.com').split(',')

# CSRF Trusted Origins for production
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')

# Check if optional packages are installed
def is_package_installed(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps (only if installed)
    'rest_framework',
    'corsheaders',

    # Local apps
    'core',
]

# Add optional apps only if installed
if is_package_installed('jazzmin'):
    INSTALLED_APPS.insert(0, 'jazzmin')
if is_package_installed('django_filters'):
    INSTALLED_APPS.insert(-1, 'django_filters')
if is_package_installed('drf_spectacular'):
    INSTALLED_APPS.insert(-1, 'drf_spectacular')
if is_package_installed('ckeditor'):
    INSTALLED_APPS.insert(-1, 'ckeditor')
    INSTALLED_APPS.insert(-1, 'ckeditor_uploader')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aquaracine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aquaracine.wsgi.application'

# Database
# Use MySQL on PythonAnywhere, SQLite for local dev
if os.environ.get('PYTHONANYWHERE_DOMAIN'):
    # PythonAnywhere MySQL configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', ''),
            'USER': os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', ''),
            'PORT': '3306',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
elif os.environ.get('DATABASE_URL'):
    # Other cloud platforms (Render, Railway)
    DATABASES = {
        'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'), conn_max_age=600)
    }
else:
    # Local development with SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Use simple storage (WhiteNoise compressed storage causes manifest issues on PythonAnywhere)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500'
).split(',')
CORS_ALLOW_ALL_ORIGINS = DEBUG

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# Add django_filters backend if installed
if is_package_installed('django_filters'):
    REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS'].insert(0, 'django_filters.rest_framework.DjangoFilterBackend')

# Add drf_spectacular schema if installed
if is_package_installed('drf_spectacular'):
    REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
    SPECTACULAR_SETTINGS = {
        'TITLE': 'Aqua-Racine API',
        'DESCRIPTION': 'API pour la gestion du site Aqua-Racine - Aquaponie en Côte d\'Ivoire',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
    }

# CKEditor Configuration (only if installed)
if is_package_installed('ckeditor'):
    CKEDITOR_UPLOAD_PATH = 'uploads/'
    CKEDITOR_CONFIGS = {
        'default': {
            'toolbar': 'full',
            'height': 300,
            'width': '100%',
        },
    }

# Email Configuration
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@aquaracine.ci')

# Jazzmin Admin Theme Configuration (only if installed)
if is_package_installed('jazzmin'):
    JAZZMIN_SETTINGS = {
        "site_title": "Aqua-Racine Admin",
        "site_header": "Aqua-Racine",
        "site_brand": "Aqua-Racine",
        "welcome_sign": "Bienvenue dans le backoffice Aqua-Racine",
        "copyright": "Aqua-Racine 2025",
        "show_sidebar": True,
        "navigation_expanded": True,
        "changeform_format": "horizontal_tabs",
    }
    JAZZMIN_UI_TWEAKS = {
        "brand_colour": "navbar-success",
        "accent": "accent-teal",
        "navbar": "navbar-dark",
        "navbar_fixed": True,
        "sidebar_fixed": True,
        "sidebar": "sidebar-dark-success",
        "theme": "default",
    }
