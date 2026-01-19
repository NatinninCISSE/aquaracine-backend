# Aqua-Racine Backend

Backend Django pour le site Aqua-Racine - Plateforme de solutions aquaponiques, hydroponiques et piscicoles.

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Lancement](#lancement)
5. [Administration](#administration)
6. [API Endpoints](#api-endpoints)
7. [Intégration Frontend](#intégration-frontend)
8. [Déploiement en Production](#déploiement-en-production)

---

## Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)

## Installation

### 1. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
cd aquaracine_backend
pip install -r requirements.txt
```

### 3. Appliquer les migrations

```bash
python manage.py makemigrations core
python manage.py migrate
```

### 4. Créer un super utilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour définir:
- Nom d'utilisateur
- Email
- Mot de passe

### 5. Collecter les fichiers statiques (production)

```bash
python manage.py collectstatic
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet backend (optionnel pour le développement):

```env
# Django
SECRET_KEY=votre-clé-secrète-très-longue-et-complexe
DEBUG=False
ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com

# Base de données (production)
DATABASE_URL=postgres://user:password@localhost:5432/aquaracine

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=Aqua-Racine <noreply@aquaracine.com>
ADMIN_EMAIL=admin@aquaracine.com
```

### Configuration des emails

Pour Gmail, vous devez:
1. Activer la validation en 2 étapes
2. Créer un mot de passe d'application
3. Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

## Lancement

### Mode développement

```bash
python manage.py runserver
```

Le serveur sera accessible sur: http://127.0.0.1:8000

### Administration

Accédez à l'interface d'administration: http://127.0.0.1:8000/admin

## Administration

L'interface d'administration permet de gérer:

### Contenu du site
- **Paramètres du site** - Logo, informations de contact, réseaux sociaux
- **Slides Hero** - Carrousel de la page d'accueil
- **Services** - Liste des services proposés
- **Avantages** - Points forts de l'entreprise

### Catalogue
- **Catégories de produits** - Organisation des produits
- **Produits** - Catalogue complet avec prix, images, descriptions

### Équipe & Blog
- **Membres de l'équipe** - Profils des membres
- **Catégories de blog** - Organisation des articles
- **Articles de blog** - Contenu éditorial

### Galerie & FAQ
- **Images de galerie** - Portfolio de réalisations
- **FAQ** - Questions fréquentes
- **Étapes du processus** - Timeline d'installation

### Demandes & Contact
- **Types d'installation** - Pisciculture, Hydroponie, Aquaponie
- **Demandes de devis** - Gestion des prospects avec workflow
- **Messages de contact** - Formulaire de contact
- **Newsletter** - Abonnés à la newsletter

### Workflow des devis

Les demandes de devis suivent un workflow précis:
1. **En attente** - Nouvelle demande reçue
2. **Contacté** - Client contacté
3. **En cours** - Projet en discussion
4. **Devis envoyé** - Proposition envoyée
5. **Accepté/Refusé** - Décision du client
6. **Terminé** - Projet finalisé

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

### Endpoints publics (GET)

| Endpoint | Description |
|----------|-------------|
| `/api/site-data/` | Toutes les données du site en une requête |
| `/api/settings/` | Paramètres du site |
| `/api/hero-slides/` | Slides du carrousel |
| `/api/services/` | Liste des services |
| `/api/products/` | Liste des produits |
| `/api/products/{id}/` | Détail d'un produit |
| `/api/product-categories/` | Catégories de produits |
| `/api/team-members/` | Membres de l'équipe |
| `/api/blog-posts/` | Articles de blog |
| `/api/blog-posts/{slug}/` | Détail d'un article |
| `/api/blog-categories/` | Catégories de blog |
| `/api/timeline-steps/` | Étapes du processus |
| `/api/gallery-images/` | Images de la galerie |
| `/api/advantages/` | Avantages |
| `/api/testimonials/` | Témoignages |
| `/api/faqs/` | Questions fréquentes |
| `/api/installation-types/` | Types d'installation |

### Endpoints POST (formulaires)

| Endpoint | Description |
|----------|-------------|
| `/api/quote-requests/` | Soumettre une demande de devis |
| `/api/contact-messages/` | Envoyer un message de contact |
| `/api/newsletter/` | S'inscrire à la newsletter |

### Exemple de requête - Demande de devis

```javascript
fetch('http://127.0.0.1:8000/api/quote-requests/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        first_name: 'Jean',
        last_name: 'Dupont',
        email: 'jean.dupont@email.com',
        phone: '+225 07 00 00 00',
        city: 'Abidjan',
        installation_types: [1, 2], // IDs des types d'installation
        project_size: 'medium',
        description: 'Je souhaite installer un système aquaponique...',
        has_water_source: true,
        has_electricity: true,
        needs_training: true,
        needs_maintenance: false
    })
})
```

## Intégration Frontend

### 1. Fichiers à inclure

Dans votre HTML, ajoutez avant `</body>`:

```html
<link rel="stylesheet" href="assets/css/quote-form.css">
<script src="assets/js/api.js"></script>
```

### 2. Configuration de l'API

Dans `api.js`, modifiez l'URL de base si nécessaire:

```javascript
const AquaRacineAPI = {
    baseUrl: 'http://127.0.0.1:8000/api', // Développement
    // baseUrl: 'https://api.aquaracine.com/api', // Production
    ...
};
```

### 3. Chargement dynamique du contenu

```javascript
// Charger toutes les données du site
document.addEventListener('DOMContentLoaded', function() {
    AquaRacineContent.loadAllContent();
});
```

### 4. Formulaire de devis

Le formulaire de devis est automatiquement géré par `AquaRacineForms.initQuoteForm()`.

## Déploiement en Production

### Option 1: VPS avec Gunicorn + Nginx

#### 1. Installer Gunicorn

```bash
pip install gunicorn
```

#### 2. Configurer Gunicorn

Créez `/etc/systemd/system/aquaracine.service`:

```ini
[Unit]
Description=Aqua-Racine Django Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/aquaracine_backend
ExecStart=/var/www/aquaracine_backend/venv/bin/gunicorn --workers 3 --bind unix:/var/www/aquaracine_backend/aquaracine.sock aquaracine.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 3. Configurer Nginx

```nginx
server {
    listen 80;
    server_name api.aquaracine.com;

    location /static/ {
        alias /var/www/aquaracine_backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/aquaracine_backend/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/aquaracine_backend/aquaracine.sock;
    }
}
```

#### 4. Activer et démarrer

```bash
sudo systemctl enable aquaracine
sudo systemctl start aquaracine
sudo systemctl restart nginx
```

### Option 2: Heroku

#### 1. Créer Procfile

```
web: gunicorn aquaracine.wsgi
```

#### 2. Créer runtime.txt

```
python-3.11.4
```

#### 3. Déployer

```bash
heroku create aquaracine-api
heroku config:set SECRET_KEY=votre-clé-secrète
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 3: PythonAnywhere

1. Créez un compte sur pythonanywhere.com
2. Uploadez le projet
3. Configurez l'application web WSGI
4. Configurez les fichiers statiques
5. Lancez les migrations

## Structure du projet

```
aquaracine_backend/
├── aquaracine/
│   ├── __init__.py
│   ├── settings.py      # Configuration Django
│   ├── urls.py          # Routes principales
│   └── wsgi.py          # Point d'entrée WSGI
├── core/
│   ├── __init__.py
│   ├── admin.py         # Configuration admin
│   ├── apps.py
│   ├── models.py        # Modèles de données
│   ├── serializers.py   # Sérialiseurs API
│   ├── urls.py          # Routes API
│   └── views.py         # Vues et ViewSets
├── templates/
│   └── emails/
│       ├── quote_confirmation.html
│       └── quote_admin_notification.html
├── media/               # Fichiers uploadés
├── staticfiles/         # Fichiers statiques collectés
├── manage.py
├── requirements.txt
└── README.md
```

## Sécurité

Avant la mise en production:

1. **Changez `SECRET_KEY`** - Générez une nouvelle clé secrète
2. **Désactivez `DEBUG`** - Mettez `DEBUG=False`
3. **Configurez `ALLOWED_HOSTS`** - Liste des domaines autorisés
4. **Utilisez HTTPS** - Certificat SSL obligatoire
5. **Sécurisez la base de données** - PostgreSQL en production

## Support

Pour toute question ou problème:
- Email: support@aquaracine.com
- Documentation API: http://127.0.0.1:8000/api/docs/

---

**Aqua-Racine** - Solutions aquaponiques durables pour l'Afrique
