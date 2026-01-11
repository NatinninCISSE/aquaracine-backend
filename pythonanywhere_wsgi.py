# +++++++++++ DJANGO +++++++++++
# Configuration WSGI pour PythonAnywhere
# Copiez ce contenu dans votre fichier WSGI sur PythonAnywhere

import os
import sys

# Ajoutez le chemin de votre projet
# REMPLACEZ 'votre_username' par votre nom d'utilisateur PythonAnywhere
path = '/home/votre_username/aquaracine-backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'aquaracine.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'True'

# Variables de base de donnees (a configurer dans l'onglet Web)
# os.environ['DB_NAME'] = 'votre_username$aquaracine'
# os.environ['DB_USER'] = 'votre_username'
# os.environ['DB_PASSWORD'] = 'votre_mot_de_passe_mysql'
# os.environ['DB_HOST'] = 'votre_username.mysql.pythonanywhere-services.com'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
