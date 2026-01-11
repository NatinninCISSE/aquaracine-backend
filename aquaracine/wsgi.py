"""
WSGI config for Aqua-Racine project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aquaracine.settings')

application = get_wsgi_application()
