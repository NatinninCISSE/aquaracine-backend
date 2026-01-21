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
# Use MySQL on PythonAnywhere if configured, otherwise SQLite
def get_database_config():
    """Get database configuration with fallback to SQLite."""
    # Check if MySQL credentials are provided
    db_name = os.environ.get('DB_NAME', '')
    db_user = os.environ.get('DB_USER', '')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', '')

    # If all MySQL credentials are provided, try to use MySQL
    if db_name and db_user and db_host:
        try:
            import MySQLdb  # noqa: F401
            return {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': db_name,
                    'USER': db_user,
                    'PASSWORD': db_password,
                    'HOST': db_host,
                    'PORT': '3306',
                    'OPTIONS': {
                        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    },
                }
            }
        except ImportError:
            pass  # MySQL driver not available, fall through to SQLite

    # Fallback to SQLite
    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

DATABASES = get_database_config()

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

# Login/Logout URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

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

# Authentication Backends - Allow login by email
AUTHENTICATION_BACKENDS = [
    'core.backends.EmailBackend',  # Custom email authentication
    'django.contrib.auth.backends.ModelBackend',  # Default username authentication as fallback
]

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
        # Title & Branding
        "site_title": "Aqua-Racine",
        "site_header": "Aqua-Racine",
        "site_brand": "Aqua-Racine",
        "site_logo": "img/aquaracinelogo3.png",
        "site_logo_classes": "img-circle",
        "site_icon": "img/aquaracinelogo3.png",
        "welcome_sign": "Bienvenue dans votre tableau de bord",
        "copyright": "Aqua-Racine © 2025",

        # Search & User
        "search_model": ["core.Product", "core.QuoteRequest", "core.ContactMessage"],
        "user_avatar": None,

        # Navigation
        "topmenu_links": [
            {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
            {"name": "Voir le site", "url": "/", "new_window": True},
            {"model": "core.quoterequest"},
            {"model": "core.contactmessage"},
        ],

        # Sidebar
        "show_sidebar": True,
        "navigation_expanded": False,
        "hide_apps": [],
        "hide_models": [],
        "order_with_respect_to": [
            "core",
            "core.sitesettings",
            "core.phonenumber",
            "core.quoterequest",
            "core.contactmessage",
            "core.newsletter",
            "core.product",
            "core.productcategory",
            "core.systemmodel",
            "core.heroslide",
            "core.service",
            "core.teammember",
            "core.galleryimage",
            "core.advantage",
            "core.testimonial",
            "core.faq",
            "core.blogpost",
            "core.blogcategory",
            "auth",
        ],

        # Icons for apps and models
        "icons": {
            "auth": "fas fa-users-cog",
            "auth.user": "fas fa-user",
            "auth.group": "fas fa-users",
            "core.sitesettings": "fas fa-cog",
            "core.phonenumber": "fas fa-phone-alt",
            "core.heroslide": "fas fa-images",
            "core.service": "fas fa-concierge-bell",
            "core.productcategory": "fas fa-tags",
            "core.product": "fas fa-fish",
            "core.teammember": "fas fa-user-tie",
            "core.blogcategory": "fas fa-folder",
            "core.blogpost": "fas fa-newspaper",
            "core.timelinestep": "fas fa-history",
            "core.galleryimage": "fas fa-camera",
            "core.advantage": "fas fa-chart-line",
            "core.testimonial": "fas fa-quote-left",
            "core.faq": "fas fa-question-circle",
            "core.installationtype": "fas fa-tools",
            "core.quoterequest": "fas fa-file-invoice-dollar",
            "core.contactmessage": "fas fa-envelope",
            "core.newsletter": "fas fa-mail-bulk",
            "core.systemmodel": "fas fa-cubes",
            "core.award": "fas fa-trophy",
            "core.fishspecies": "fas fa-fish",
            "core.croptype": "fas fa-seedling",
            "core.basintype": "fas fa-water",
            "core.hydrosystemtype": "fas fa-tint",
            "core.trainingtype": "fas fa-graduation-cap",
            "core.quizquestion": "fas fa-question",
            "core.gameprize": "fas fa-gift",
            "core.gameparticipation": "fas fa-gamepad",
        },
        "default_icon_parents": "fas fa-folder",
        "default_icon_children": "fas fa-circle",

        # UI Options
        "related_modal_active": True,
        "custom_css": None,  # Désactivé - styles dans base_site.html
        "custom_js": None,
        "use_google_fonts_cdn": True,
        "show_ui_builder": False,
        "changeform_format": "horizontal_tabs",
        "changeform_format_overrides": {
            "auth.user": "collapsible",
            "core.quoterequest": "vertical_tabs",
        },
    }

    JAZZMIN_UI_TWEAKS = {
        "navbar_small_text": False,
        "footer_small_text": False,
        "body_small_text": False,
        "brand_small_text": False,
        "brand_colour": "navbar-success",
        "accent": "accent-success",
        "navbar": "navbar-success navbar-dark",
        "no_navbar_border": False,
        "navbar_fixed": True,
        "layout_boxed": False,
        "footer_fixed": False,
        "sidebar_fixed": True,
        "sidebar": "sidebar-light-success",
        "sidebar_nav_small_text": False,
        "sidebar_disable_expand": False,
        "sidebar_nav_child_indent": True,
        "sidebar_nav_compact_style": False,
        "sidebar_nav_legacy_style": False,
        "sidebar_nav_flat_style": False,
        "theme": "default",
        "dark_mode_theme": None,
        "button_classes": {
            "primary": "btn-success",
            "secondary": "btn-secondary",
            "info": "btn-info",
            "warning": "btn-warning",
            "danger": "btn-danger",
            "success": "btn-success",
        },
    }
