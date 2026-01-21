"""
Models for Aqua-Racine website management.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# CKEditor est optionnel - utiliser TextField comme fallback
try:
    from ckeditor.fields import RichTextField
except ImportError:
    RichTextField = models.TextField


# ============================================
# USER PROFILE WITH ROLES
# ============================================

class UserProfile(models.Model):
    """Extended user profile with roles for admin panel."""

    ROLE_CHOICES = [
        ('super_admin', 'Super Administrateur'),
        ('admin', 'Administrateur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        'Rôle',
        max_length=20,
        choices=ROLE_CHOICES,
        default='admin'
    )
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    avatar = models.ImageField('Photo de profil', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('Date de création', auto_now_add=True)
    updated_at = models.DateTimeField('Dernière modification', auto_now=True)

    class Meta:
        verbose_name = 'Profil Utilisateur'
        verbose_name_plural = 'Profils Utilisateurs'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == 'super_admin' or self.user.is_superuser

    @property
    def is_simple_admin(self):
        return self.role == 'admin' and not self.user.is_superuser

    def save(self, *args, **kwargs):
        # Sync role with Django permissions (avoid recursion)
        update_user = False
        if self.role == 'super_admin':
            if not self.user.is_superuser or not self.user.is_staff:
                self.user.is_superuser = True
                self.user.is_staff = True
                update_user = True
        elif self.role == 'admin':
            if not self.user.is_staff:
                self.user.is_staff = True
                update_user = True

        # Only save user if we made changes (prevent recursion)
        if update_user and self.pk:  # Only if profile already exists
            User.objects.filter(pk=self.user.pk).update(
                is_superuser=self.user.is_superuser,
                is_staff=self.user.is_staff
            )

        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created."""
    if instance.is_staff:
        role = 'super_admin' if instance.is_superuser else 'admin'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Global site settings - singleton model."""
    site_name = models.CharField(max_length=100, default="Aqua-Racine", verbose_name="Nom du site")
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Logo du site")
    site_favicon = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Favicon")

    # Contact Information
    phone = models.CharField(max_length=100, default="+225 07 67 20 35 32 / +225 07 07 36 18 79 / +225 07 47 46 77 73", verbose_name="Téléphone")
    email = models.EmailField(default="aquaracine@gmail.com", verbose_name="Email")
    address = models.TextField(default="Abidjan, Côte d'Ivoire", verbose_name="Adresse")

    # Social Media
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter/X")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube")

    # About Section
    about_title = models.CharField(max_length=200, default="À propos d'Aqua-Racine", verbose_name="Titre À propos")
    about_description = RichTextField(blank=True, verbose_name="Description À propos")
    about_video_url = models.URLField(blank=True, verbose_name="URL vidéo À propos")
    about_image_1 = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name="Image À propos 1")
    about_image_2 = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name="Image À propos 2")
    about_image_3 = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name="Image À propos 3")

    # Footer
    footer_text = models.TextField(default="© 2025 Aqua-Racine. Tous droits réservés.", verbose_name="Texte du footer")

    # SEO
    meta_description = models.TextField(blank=True, verbose_name="Meta description")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Mots-clés SEO")

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PhoneNumber(models.Model):
    """Multiple phone numbers for the site."""
    number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    label = models.CharField(max_length=50, blank=True, verbose_name="Libellé",
                            help_text="Ex: Principal, WhatsApp, Service client")
    is_whatsapp = models.BooleanField(default=False, verbose_name="WhatsApp")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Numéro de téléphone"
        verbose_name_plural = "Numéros de téléphone"
        ordering = ['order']

    def __str__(self):
        if self.label:
            return f"{self.number} ({self.label})"
        return self.number

    @property
    def tel_link(self):
        """Returns the phone number formatted for tel: links (no spaces)."""
        return self.number.replace(" ", "").replace("-", "")


class HeroSlide(TimeStampedModel):
    """Hero section carousel slides."""
    title = models.CharField(max_length=200, verbose_name="Titre")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="Sous-titre")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='hero/', verbose_name="Image de fond")
    button_text = models.CharField(max_length=50, default="En savoir plus", verbose_name="Texte du bouton")
    button_url = models.CharField(max_length=200, default="#about", verbose_name="Lien du bouton")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Slide Hero"
        verbose_name_plural = "Slides Hero"
        ordering = ['order']

    def __str__(self):
        return self.title


class Service(TimeStampedModel):
    """Services offered by Aqua-Racine."""
    COLOR_CHOICES = [
        ('#00bcd4,#0097a7', 'Cyan'),
        ('#4caf50,#2e7d32', 'Vert'),
        ('#1976d2,#0d47a1', 'Bleu'),
        ('#ff9800,#f57c00', 'Orange'),
        ('#9c27b0,#7b1fa2', 'Violet'),
        ('#e91e63,#c2185b', 'Rose'),
        ('#607d8b,#455a64', 'Gris'),
        ('#f44336,#c62828', 'Rouge'),
        ('#795548,#4e342e', 'Marron'),
    ]
    title = models.CharField(max_length=100, verbose_name="Titre du service")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=50, default="fa fa-leaf", verbose_name="Classe icône (FontAwesome)",
                           help_text="Ex: fa fa-leaf, fa fa-cogs, fa fa-graduation-cap")
    color = models.CharField(max_length=30, choices=COLOR_CHOICES, default='#4caf50,#2e7d32',
                            verbose_name="Couleur du dégradé")
    link_url = models.CharField(max_length=200, blank=True, verbose_name="URL du lien",
                               help_text="Ex: /devis/aquaponie/ ou #contact")
    link_text = models.CharField(max_length=50, default="En savoir plus", verbose_name="Texte du lien")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Image")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    @property
    def gradient_style(self):
        """Returns CSS gradient style for the icon background."""
        colors = self.color.split(',')
        if len(colors) == 2:
            return f"linear-gradient(135deg, {colors[0]}, {colors[1]})"
        return f"linear-gradient(135deg, {self.color}, {self.color})"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order']

    def __str__(self):
        return self.title


class ProductCategory(TimeStampedModel):
    """Product categories."""
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug URL")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Image")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    """Products sold by Aqua-Racine."""
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug URL")
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Catégorie"
    )
    description = models.TextField(verbose_name="Description courte")
    full_description = RichTextField(blank=True, verbose_name="Description complète")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (FCFA)")
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        verbose_name="Ancien prix (barré)"
    )
    image = models.ImageField(upload_to='products/', verbose_name="Image principale")
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Image 2")
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Image 3")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    unit = models.CharField(max_length=20, default="kg", verbose_name="Unité (kg, pièce, etc.)")
    is_featured = models.BooleanField(default=False, verbose_name="Produit vedette")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0


class TeamMember(TimeStampedModel):
    """Team members."""
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    role = models.CharField(max_length=100, verbose_name="Poste/Rôle")
    bio = models.TextField(blank=True, verbose_name="Biographie")
    photo = models.ImageField(upload_to='team/', verbose_name="Photo")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter/X")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.role}"


class BlogCategory(TimeStampedModel):
    """Blog categories."""
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug URL")

    class Meta:
        verbose_name = "Catégorie de blog"
        verbose_name_plural = "Catégories de blog"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(TimeStampedModel):
    """Blog posts/articles."""
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug URL")
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name="Catégorie"
    )
    excerpt = models.TextField(verbose_name="Extrait/Résumé")
    content = RichTextField(verbose_name="Contenu")
    image = models.ImageField(upload_to='blog/', verbose_name="Image principale")
    author_name = models.CharField(max_length=100, default="Aqua-Racine", verbose_name="Auteur")
    author_photo = models.ImageField(upload_to='blog/authors/', blank=True, null=True, verbose_name="Photo auteur")
    views = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    is_featured = models.BooleanField(default=False, verbose_name="Article vedette")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    published_date = models.DateField(auto_now_add=True, verbose_name="Date de publication")

    class Meta:
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class TimelineStep(TimeStampedModel):
    """Timeline/Process steps for explaining aquaponics."""
    title = models.CharField(max_length=100, verbose_name="Titre de l'étape")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=50, default="fa fa-check", verbose_name="Classe icône")
    image = models.ImageField(upload_to='timeline/', blank=True, null=True, verbose_name="Image")
    video_url = models.URLField(blank=True, verbose_name="URL vidéo")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Étape du processus"
        verbose_name_plural = "Étapes du processus"
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"


class GalleryImage(TimeStampedModel):
    """Gallery images for the portfolio/gallery section."""
    title = models.CharField(max_length=100, verbose_name="Titre")
    image = models.ImageField(upload_to='gallery/', verbose_name="Image")
    category = models.CharField(max_length=50, default="aquaponie", verbose_name="Catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Image de galerie"
        verbose_name_plural = "Images de galerie"
        ordering = ['order']

    def __str__(self):
        return self.title


class Advantage(TimeStampedModel):
    """Advantages/Benefits with percentage indicators."""
    title = models.CharField(max_length=100, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    percentage = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage"
    )
    icon = models.CharField(max_length=50, default="fa fa-leaf", verbose_name="Classe icône")
    color = models.CharField(max_length=20, default="#4CAF50", verbose_name="Couleur")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Avantage"
        verbose_name_plural = "Avantages"
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.percentage}%)"


class Testimonial(TimeStampedModel):
    """Client testimonials."""
    name = models.CharField(max_length=100, verbose_name="Nom")
    role = models.CharField(max_length=100, blank=True, verbose_name="Fonction/Entreprise")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="Photo")
    content = models.TextField(verbose_name="Témoignage")
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (1-5)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.rating}/5"


class FAQ(TimeStampedModel):
    """Frequently Asked Questions."""
    question = models.CharField(max_length=300, verbose_name="Question")
    answer = RichTextField(verbose_name="Réponse")
    category = models.CharField(max_length=50, default="general", verbose_name="Catégorie")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Question fréquente"
        verbose_name_plural = "Questions fréquentes"
        ordering = ['order']

    def __str__(self):
        return self.question[:50]


class InstallationType(models.Model):
    """Types of installations for quote requests."""
    name = models.CharField(max_length=100, verbose_name="Type d'installation")
    description = models.TextField(blank=True, verbose_name="Description")
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name="Prix de base (FCFA)"
    )
    icon = models.CharField(max_length=50, default="fa fa-fish", verbose_name="Classe icône")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Type d'installation"
        verbose_name_plural = "Types d'installations"
        ordering = ['order']

    def __str__(self):
        return self.name


class QuoteRequest(TimeStampedModel):
    """Quote/Devis requests for installations."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONTACTED = 'contacted', 'Contacté'
        IN_PROGRESS = 'in_progress', 'En cours de traitement'
        QUOTED = 'quoted', 'Devis envoyé'
        ACCEPTED = 'accepted', 'Accepté'
        REJECTED = 'rejected', 'Refusé'
        COMPLETED = 'completed', 'Terminé'

    class ProjectSize(models.TextChoices):
        SMALL = 'small', 'Petit (usage personnel/familial)'
        MEDIUM = 'medium', 'Moyen (petite exploitation)'
        LARGE = 'large', 'Grand (exploitation commerciale)'
        INDUSTRIAL = 'industrial', 'Industriel'

    # Contact Information
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    company = models.CharField(max_length=100, blank=True, verbose_name="Entreprise/Organisation")

    # Location
    city = models.CharField(max_length=100, verbose_name="Ville")
    address = models.TextField(blank=True, verbose_name="Adresse complète")

    # Project Details
    installation_types = models.ManyToManyField(
        InstallationType,
        related_name='quote_requests',
        verbose_name="Types d'installation souhaités"
    )
    project_size = models.CharField(
        max_length=20,
        choices=ProjectSize.choices,
        default=ProjectSize.SMALL,
        verbose_name="Taille du projet"
    )
    surface_area = models.CharField(max_length=50, blank=True, verbose_name="Surface disponible (m²)")
    budget_range = models.CharField(max_length=100, blank=True, verbose_name="Budget estimé")
    timeline = models.CharField(max_length=100, blank=True, verbose_name="Délai souhaité")

    # Additional Information
    description = models.TextField(verbose_name="Description du projet")
    has_water_source = models.BooleanField(default=False, verbose_name="Source d'eau disponible")
    has_electricity = models.BooleanField(default=False, verbose_name="Électricité disponible")
    needs_training = models.BooleanField(default=False, verbose_name="Formation souhaitée")
    needs_maintenance = models.BooleanField(default=False, verbose_name="Contrat maintenance souhaité")

    # Files
    attachment = models.FileField(
        upload_to='quotes/attachments/',
        blank=True, null=True,
        verbose_name="Pièce jointe (plan, photo, etc.)"
    )

    # Processing
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )
    admin_notes = models.TextField(blank=True, verbose_name="Notes internes")
    estimated_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name="Montant estimé (FCFA)"
    )
    assigned_to = models.CharField(max_length=100, blank=True, verbose_name="Assigné à")

    class Meta:
        verbose_name = "Demande de devis"
        verbose_name_plural = "Demandes de devis"
        ordering = ['-created_at']

    def __str__(self):
        return f"Devis #{self.pk} - {self.first_name} {self.last_name} ({self.get_status_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ContactMessage(TimeStampedModel):
    """Contact form messages."""

    class Status(models.TextChoices):
        NEW = 'new', 'Nouveau'
        READ = 'read', 'Lu'
        REPLIED = 'replied', 'Répondu'
        ARCHIVED = 'archived', 'Archivé'

    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Statut"
    )
    admin_notes = models.TextField(blank=True, verbose_name="Notes internes")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'Sans sujet'}"


class Newsletter(TimeStampedModel):
    """Newsletter subscribers."""
    email = models.EmailField(unique=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class SystemModel(TimeStampedModel):
    """Pre-defined system models for aquaponics, hydroponics, and fish farming."""

    class SystemType(models.TextChoices):
        AQUAPONICS = 'aquaponie', 'Aquaponie'
        HYDROPONICS = 'hydroponie', 'Hydroponie'
        FISH_FARMING = 'pisciculture', 'Pisciculture'

    name = models.CharField(max_length=200, verbose_name="Nom du modèle")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug URL")
    system_type = models.CharField(
        max_length=20,
        choices=SystemType.choices,
        default=SystemType.AQUAPONICS,
        verbose_name="Type de système"
    )
    description = models.TextField(verbose_name="Description")
    full_description = RichTextField(blank=True, verbose_name="Description complète")

    # Dimensions
    length = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Longueur (m)")
    width = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Largeur (m)")
    height = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Hauteur (m)")

    # Capacity
    fish_capacity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Capacité poissons")
    plant_capacity = models.PositiveIntegerField(blank=True, null=True, verbose_name="Capacité plantes")
    water_volume = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Volume d'eau (L)")

    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix (FCFA)")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Ancien prix (barré)")

    # Images
    image = models.ImageField(upload_to='systems/', verbose_name="Image principale")
    image_2 = models.ImageField(upload_to='systems/', blank=True, null=True, verbose_name="Image 2")
    image_3 = models.ImageField(upload_to='systems/', blank=True, null=True, verbose_name="Image 3")

    # Features
    features = models.TextField(blank=True, verbose_name="Caractéristiques (une par ligne)")
    includes = models.TextField(blank=True, verbose_name="Inclus dans le kit (un par ligne)")

    # Target
    target_audience = models.CharField(max_length=100, default="Ménages", verbose_name="Public cible")

    # Status
    is_featured = models.BooleanField(default=False, verbose_name="Modèle vedette")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Modèle de système"
        verbose_name_plural = "Modèles de systèmes"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_system_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def dimensions(self):
        return f"{self.length} x {self.width} x {self.height} m"

    @property
    def features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []

    @property
    def includes_list(self):
        if self.includes:
            return [i.strip() for i in self.includes.split('\n') if i.strip()]
        return []


# ============================================
# OPTIONS DYNAMIQUES POUR FORMULAIRES DE DEVIS
# ============================================

class FishSpecies(models.Model):
    """Espèces de poissons disponibles pour l'élevage."""
    name = models.CharField(max_length=100, verbose_name="Nom de l'espèce")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='fish/', blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Espèce de poisson"
        verbose_name_plural = "Espèces de poissons"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class CropType(models.Model):
    """Types de cultures/légumes pour hydroponie."""
    name = models.CharField(max_length=100, verbose_name="Nom de la culture")
    category = models.CharField(max_length=50, default="légume", verbose_name="Catégorie",
                                help_text="Ex: légume, fruit, herbe aromatique")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='crops/', blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Type de culture"
        verbose_name_plural = "Types de cultures"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class BasinType(models.Model):
    """Types de bassins pour pisciculture."""
    name = models.CharField(max_length=100, verbose_name="Type de bassin")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='basins/', blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Type de bassin"
        verbose_name_plural = "Types de bassins"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class HydroSystemType(models.Model):
    """Types de systèmes hydroponiques."""
    name = models.CharField(max_length=100, verbose_name="Type de système")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code",
                           help_text="Ex: NFT, DWC, tours, etc.")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='hydro_systems/', blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Type de système hydroponique"
        verbose_name_plural = "Types de systèmes hydroponiques"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class TrainingType(models.Model):
    """Types de formations disponibles."""
    name = models.CharField(max_length=100, verbose_name="Nom de la formation")
    category = models.CharField(max_length=50, verbose_name="Catégorie",
                                help_text="Ex: pisciculture, hydroponie, aquaponie")
    description = models.TextField(blank=True, verbose_name="Description")
    duration = models.CharField(max_length=50, blank=True, verbose_name="Durée estimée")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                               verbose_name="Prix indicatif (FCFA)")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Type de formation"
        verbose_name_plural = "Types de formations"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Award(TimeStampedModel):
    """Awards, distinctions and prizes won by the team."""
    title = models.CharField(max_length=200, verbose_name="Titre du prix/distinction")
    organization = models.CharField(max_length=200, verbose_name="Organisation/Concours")
    description = models.TextField(blank=True, verbose_name="Description")
    year = models.PositiveIntegerField(verbose_name="Année")
    image = models.ImageField(upload_to='awards/', blank=True, null=True, verbose_name="Image/Logo")
    certificate = models.ImageField(upload_to='awards/certificates/', blank=True, null=True, verbose_name="Certificat/Diplôme")
    url = models.URLField(blank=True, verbose_name="Lien externe")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Distinction/Prix"
        verbose_name_plural = "Distinctions et Prix"
        ordering = ['-year', 'order']

    def __str__(self):
        return f"{self.title} ({self.year})"


class QuizQuestion(TimeStampedModel):
    """Questions for the quiz game - manageable from admin."""
    question = models.CharField(max_length=500, verbose_name="Question")
    option_1 = models.CharField(max_length=300, verbose_name="Option 1")
    option_2 = models.CharField(max_length=300, verbose_name="Option 2")
    option_3 = models.CharField(max_length=300, verbose_name="Option 3")
    option_4 = models.CharField(max_length=300, verbose_name="Option 4")
    correct_option = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Réponse correcte (1-4)",
        help_text="Numéro de l'option correcte (1, 2, 3 ou 4)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Question du quiz"
        verbose_name_plural = "Questions du quiz"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question[:80] + ('...' if len(self.question) > 80 else '')

    @property
    def options(self):
        """Returns all options as a list."""
        return [self.option_1, self.option_2, self.option_3, self.option_4]

    @property
    def correct_index(self):
        """Returns the correct option index (0-based for frontend)."""
        return self.correct_option - 1


class GamePrize(TimeStampedModel):
    """Prizes for the wheel game - manageable from admin."""
    PRIZE_TYPE_CHOICES = [
        ('discount', 'Réduction (%)'),
        ('free_delivery', 'Livraison gratuite'),
        ('free_item', 'Article gratuit'),
        ('lost', 'Pas de chance'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom du prix")
    prize_type = models.CharField(max_length=20, choices=PRIZE_TYPE_CHOICES, default='discount', verbose_name="Type de prix")
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage de réduction",
        help_text="Uniquement pour les prix de type 'Réduction'"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    color = models.CharField(max_length=7, default='#4caf50', verbose_name="Couleur sur la roue",
                            help_text="Code couleur hex (ex: #4caf50)")
    icon = models.CharField(max_length=10, default='🎁', verbose_name="Emoji/Icône")
    applies_to_fresh_products_only = models.BooleanField(
        default=True,
        verbose_name="Applicable uniquement aux produits frais",
        help_text="Si coché, la réduction ne s'applique qu'aux produits frais"
    )
    is_winning_prize = models.BooleanField(default=True, verbose_name="Est un prix gagnant",
                                           help_text="Décochez pour les cases 'Pas de chance'")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=0, verbose_name="Position sur la roue (0-7)")

    class Meta:
        verbose_name = "Prix de la roue"
        verbose_name_plural = "Prix de la roue"
        ordering = ['order']

    def __str__(self):
        if self.prize_type == 'discount':
            return f"{self.name} ({self.discount_percent}%)"
        return self.name

    @property
    def display_name(self):
        """Name to display on the wheel."""
        if self.prize_type == 'discount':
            return f"-{self.discount_percent}%"
        elif self.prize_type == 'lost':
            return "Pas de chance"
        return self.name


class GameParticipation(TimeStampedModel):
    """Track quiz and wheel game participations."""
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")

    quiz_score = models.PositiveIntegerField(default=0, verbose_name="Score au quiz")
    quiz_total = models.PositiveIntegerField(default=4, verbose_name="Nombre de questions")

    prize = models.ForeignKey(
        GamePrize,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='participations',
        verbose_name="Prix gagné"
    )
    promo_code = models.CharField(max_length=20, blank=True, verbose_name="Code promo")

    has_used_prize = models.BooleanField(default=False, verbose_name="Prix utilisé")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")

    class Meta:
        verbose_name = "Participation au jeu"
        verbose_name_plural = "Participations au jeu"
        ordering = ['-created_at']

    def __str__(self):
        prize_display = self.get_prize_won_display() if self.prize_won else "En attente"
        return f"{self.name} - {prize_display} ({self.created_at.strftime('%d/%m/%Y')})"

    @classmethod
    def has_already_played(cls, email=None, phone=None):
        """Check if email or phone has already participated."""
        if email and cls.objects.filter(email__iexact=email).exists():
            return True
        if phone and cls.objects.filter(phone=phone).exists():
            return True
        return False
