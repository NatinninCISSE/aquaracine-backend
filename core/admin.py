"""
Admin configuration for Aqua-Racine backoffice.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import (
    SiteSettings, PhoneNumber, HeroSlide, Service, ProductCategory, Product,
    TeamMember, BlogCategory, BlogPost, TimelineStep, GalleryImage,
    Advantage, Testimonial, FAQ, InstallationType, QuoteRequest,
    ContactMessage, Newsletter, SystemModel, Award,
    FishSpecies, CropType, BasinType, HydroSystemType, TrainingType,
    QuizQuestion, GamePrize, GameParticipation
)


# ============================================
# PHONE NUMBERS
# ============================================

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    """Admin for phone numbers."""

    list_display = ['number', 'label', 'is_whatsapp', 'order', 'is_active']
    list_filter = ['is_whatsapp', 'is_active']
    list_editable = ['label', 'is_whatsapp', 'order', 'is_active']
    search_fields = ['number', 'label']
    ordering = ['order']

    fieldsets = (
        (None, {
            'fields': ('number', 'label', 'is_whatsapp'),
            'description': 'Ajoutez autant de numéros que vous souhaitez. Ils seront affichés dans l\'en-tête du site.'
        }),
        ('Options', {
            'fields': ('order', 'is_active')
        }),
    )


# ============================================
# SITE SETTINGS
# ============================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin for site settings (singleton)."""

    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'site_logo', 'site_favicon'),
            'description': 'Paramètres de base du site'
        }),
        ('Coordonnées', {
            'fields': ('phone', 'email', 'address'),
            'description': 'Informations de contact affichées sur le site'
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'linkedin_url', 'twitter_url', 'instagram_url', 'youtube_url'),
            'classes': ('collapse',),
            'description': 'Liens vers vos réseaux sociaux'
        }),
        ('Section À propos (Page d\'accueil)', {
            'fields': ('about_title', 'about_description', 'about_video_url', 'about_image_1', 'about_image_2', 'about_image_3'),
            'description': 'Contenu de la section "À propos" visible sur la page d\'accueil. Modifiez le titre et la description ici.'
        }),
        ('Footer & SEO', {
            'fields': ('footer_text', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
            'description': 'Texte du pied de page et paramètres SEO'
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Automatically redirect to the singleton object
        obj = SiteSettings.get_settings()
        from django.shortcuts import redirect
        return redirect(f'/admin/core/sitesettings/{obj.pk}/change/')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = True
        return super().change_view(request, object_id, form_url, extra_context)


# ============================================
# HERO SLIDES
# ============================================

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    """Admin for hero carousel slides."""

    list_display = ['title', 'image_preview', 'order', 'is_active', 'updated_at']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'subtitle', 'description']
    ordering = ['order']

    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Bouton', {
            'fields': ('button_text', 'button_url')
        }),
        ('Options', {
            'fields': ('order', 'is_active')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit:cover;border-radius:4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Aperçu"


# ============================================
# SERVICES
# ============================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin for services."""

    list_display = ['title', 'icon_preview', 'image_preview', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order']

    def icon_preview(self, obj):
        return format_html('<i class="{}" style="font-size:24px;"></i>', obj.icon)
    icon_preview.short_description = "Icône"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


# ============================================
# PRODUCTS
# ============================================

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin for product categories."""

    list_display = ['name', 'slug', 'product_count', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']

    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = "Produits"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for products."""

    list_display = ['image_preview', 'name', 'category', 'price_display', 'stock', 'is_featured', 'is_active']
    list_filter = ['category', 'is_featured', 'is_active']
    list_editable = ['is_featured', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['category']
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'category', 'description', 'full_description')
        }),
        ('Prix et stock', {
            'fields': ('price', 'old_price', 'stock', 'unit')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_3')
        }),
        ('Options', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"

    def price_display(self, obj):
        if obj.old_price:
            return format_html('<del style="color:#999;">{} FCFA</del><br><strong>{} FCFA</strong>', obj.old_price, obj.price)
        return f"{obj.price} FCFA"
    price_display.short_description = "Prix"


# ============================================
# TEAM
# ============================================

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin for team members."""

    list_display = ['photo_preview', 'name', 'role', 'email', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'role', 'bio']
    ordering = ['order']

    fieldsets = (
        ('Informations', {
            'fields': ('name', 'role', 'bio', 'photo')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Réseaux sociaux', {
            'fields': ('linkedin_url', 'facebook_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('order', 'is_active')
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:50%;"/>', obj.photo.url)
        return "-"
    photo_preview.short_description = "Photo"


# ============================================
# BLOG
# ============================================

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Admin for blog categories."""

    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.posts.filter(is_published=True).count()
    post_count.short_description = "Articles"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin for blog posts."""

    list_display = ['image_preview', 'title', 'category', 'author_name', 'views', 'is_featured', 'is_published', 'published_date']
    list_filter = ['category', 'is_featured', 'is_published', 'published_date']
    list_editable = ['is_featured', 'is_published']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['category']
    date_hierarchy = 'published_date'
    ordering = ['-published_date']

    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'content', 'image')
        }),
        ('Auteur', {
            'fields': ('author_name', 'author_photo')
        }),
        ('Options', {
            'fields': ('is_featured', 'is_published')
        }),
    )

    readonly_fields = ['views']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="50" style="object-fit:cover;border-radius:4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


# ============================================
# TIMELINE
# ============================================

@admin.register(TimelineStep)
class TimelineStepAdmin(admin.ModelAdmin):
    """Admin for timeline/process steps."""

    list_display = ['order', 'title', 'has_image', 'has_video', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['order']

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Image"

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = "Vidéo"


# ============================================
# GALLERY
# ============================================

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Admin for gallery images."""

    list_display = ['image_preview', 'title', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="60" style="object-fit:cover;border-radius:4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Aperçu"


# ============================================
# ADVANTAGES
# ============================================

@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    """Admin for advantages with percentage."""

    list_display = ['title', 'percentage_display', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order']

    def percentage_display(self, obj):
        color = obj.color or '#4CAF50'
        return format_html(
            '<div style="width:100px;background:#e0e0e0;border-radius:10px;overflow:hidden;">'
            '<div style="width:{}%;background:{};padding:2px 8px;color:white;font-size:12px;text-align:center;">'
            '{}%</div></div>',
            obj.percentage, color, obj.percentage
        )
    percentage_display.short_description = "Pourcentage"


# ============================================
# TESTIMONIALS
# ============================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for testimonials."""

    list_display = ['photo_preview', 'name', 'role', 'rating_stars', 'order', 'is_active']
    list_filter = ['rating', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'role', 'content']
    ordering = ['order']

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%;"/>', obj.photo.url)
        return "-"
    photo_preview.short_description = "Photo"

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:#ffc107;font-size:16px;">{}</span>', stars)
    rating_stars.short_description = "Note"


# ============================================
# FAQ
# ============================================

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin for FAQs."""

    list_display = ['question_short', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'answer']
    ordering = ['order']

    def question_short(self, obj):
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
    question_short.short_description = "Question"


# ============================================
# INSTALLATION TYPES
# ============================================

@admin.register(InstallationType)
class InstallationTypeAdmin(admin.ModelAdmin):
    """Admin for installation types."""

    list_display = ['name', 'base_price_display', 'icon', 'quote_count', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order']

    def base_price_display(self, obj):
        if obj.base_price:
            return f"{obj.base_price:,.0f} FCFA"
        return "-"
    base_price_display.short_description = "Prix de base"

    def quote_count(self, obj):
        return obj.quote_requests.count()
    quote_count.short_description = "Demandes"


# ============================================
# QUOTE REQUESTS
# ============================================

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    """Admin for quote requests."""

    list_display = ['id', 'full_name', 'email', 'phone', 'city', 'installation_list', 'project_size', 'status_badge', 'created_at']
    list_filter = ['status', 'project_size', 'installation_types', 'city', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'city', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    filter_horizontal = ['installation_types']

    fieldsets = (
        ('Contact', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company')
        }),
        ('Localisation', {
            'fields': ('city', 'address')
        }),
        ('Projet', {
            'fields': ('installation_types', 'project_size', 'surface_area', 'budget_range', 'timeline', 'description')
        }),
        ('Infrastructure', {
            'fields': ('has_water_source', 'has_electricity', 'needs_training', 'needs_maintenance')
        }),
        ('Pièce jointe', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Traitement', {
            'fields': ('status', 'assigned_to', 'estimated_amount', 'admin_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = "Nom"

    def installation_list(self, obj):
        types = obj.installation_types.all()[:3]
        names = [t.name for t in types]
        if obj.installation_types.count() > 3:
            names.append('...')
        return ', '.join(names)
    installation_list.short_description = "Types"

    def status_badge(self, obj):
        colors = {
            'pending': '#6c757d',
            'contacted': '#17a2b8',
            'in_progress': '#ffc107',
            'quoted': '#007bff',
            'accepted': '#28a745',
            'rejected': '#dc3545',
            'completed': '#20c997',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Statut"

    actions = ['mark_contacted', 'mark_in_progress', 'mark_quoted']

    def mark_contacted(self, request, queryset):
        queryset.update(status='contacted')
    mark_contacted.short_description = "Marquer comme contacté"

    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_in_progress.short_description = "Marquer en cours de traitement"

    def mark_quoted(self, request, queryset):
        queryset.update(status='quoted')
    mark_quoted.short_description = "Marquer comme devis envoyé"


# ============================================
# CONTACT MESSAGES
# ============================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin for contact messages."""

    list_display = ['name', 'email', 'subject_short', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Message', {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Traitement', {
            'fields': ('status', 'admin_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def subject_short(self, obj):
        return obj.subject[:50] + '...' if obj.subject and len(obj.subject) > 50 else (obj.subject or 'Sans sujet')
    subject_short.short_description = "Sujet"

    def status_badge(self, obj):
        colors = {
            'new': '#dc3545',
            'read': '#17a2b8',
            'replied': '#28a745',
            'archived': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Statut"

    actions = ['mark_read', 'mark_replied', 'mark_archived']

    def mark_read(self, request, queryset):
        queryset.update(status='read')
    mark_read.short_description = "Marquer comme lu"

    def mark_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_replied.short_description = "Marquer comme répondu"

    def mark_archived(self, request, queryset):
        queryset.update(status='archived')
    mark_archived.short_description = "Archiver"


# ============================================
# NEWSLETTER
# ============================================

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin for newsletter subscribers."""

    list_display = ['email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    actions = ['export_emails', 'deactivate', 'activate']

    def export_emails(self, request, queryset):
        # This would export emails - just a placeholder action
        self.message_user(request, f"{queryset.count()} emails sélectionnés pour export")
    export_emails.short_description = "Exporter les emails"

    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = "Désactiver"

    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = "Activer"


# ============================================
# SYSTEM MODELS (Pre-defined systems)
# ============================================

@admin.register(SystemModel)
class SystemModelAdmin(admin.ModelAdmin):
    """Admin for pre-defined system models."""

    list_display = ['image_preview', 'name', 'system_type', 'dimensions_display', 'price_display', 'target_audience', 'is_featured', 'is_active', 'order']
    list_filter = ['system_type', 'is_featured', 'is_active', 'target_audience']
    list_editable = ['is_featured', 'is_active', 'order']
    search_fields = ['name', 'description', 'target_audience']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'system_type', 'description', 'full_description')
        }),
        ('Dimensions', {
            'fields': ('length', 'width', 'height')
        }),
        ('Capacités', {
            'fields': ('fish_capacity', 'plant_capacity', 'water_volume'),
            'classes': ('collapse',)
        }),
        ('Prix', {
            'fields': ('price', 'old_price')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_3')
        }),
        ('Caractéristiques', {
            'fields': ('features', 'includes'),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('target_audience', 'is_featured', 'is_active', 'order')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"

    def dimensions_display(self, obj):
        return obj.dimensions
    dimensions_display.short_description = "Dimensions"

    def price_display(self, obj):
        if obj.old_price:
            old_price_fmt = f"{obj.old_price:,.0f}".replace(",", " ")
            price_fmt = f"{obj.price:,.0f}".replace(",", " ")
            return format_html('<del style="color:#999;">{} FCFA</del><br><strong style="color:#2e7d32;">{} FCFA</strong>', old_price_fmt, price_fmt)
        price_fmt = f"{obj.price:,.0f}".replace(",", " ")
        return format_html('<strong>{} FCFA</strong>', price_fmt)
    price_display.short_description = "Prix"


# ============================================
# AWARDS (Distinctions et Prix)
# ============================================

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    """Admin for awards and distinctions."""

    list_display = ['image_preview', 'title', 'organization', 'year', 'order', 'is_active']
    list_filter = ['year', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'organization', 'description']
    ordering = ['-year', 'order']

    fieldsets = (
        ('Informations', {
            'fields': ('title', 'organization', 'year', 'description')
        }),
        ('Médias', {
            'fields': ('image', 'certificate', 'url')
        }),
        ('Options', {
            'fields': ('order', 'is_active')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


# ============================================
# GAMIFICATION - QUIZ & ROUE
# ============================================

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Admin for quiz questions - CRUD from backoffice."""

    list_display = ['question_short', 'correct_answer_preview', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'option_1', 'option_2', 'option_3', 'option_4']
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Question', {
            'fields': ('question',),
            'description': 'Écrivez la question du quiz'
        }),
        ('Options de réponse', {
            'fields': ('option_1', 'option_2', 'option_3', 'option_4'),
            'description': 'Entrez les 4 options de réponse possibles'
        }),
        ('Réponse correcte', {
            'fields': ('correct_option',),
            'description': 'Indiquez le numéro de l\'option correcte (1, 2, 3 ou 4)'
        }),
        ('Options', {
            'fields': ('order', 'is_active')
        }),
    )

    def question_short(self, obj):
        return obj.question[:60] + '...' if len(obj.question) > 60 else obj.question
    question_short.short_description = "Question"

    def correct_answer_preview(self, obj):
        options = obj.options
        correct_idx = obj.correct_option - 1
        if 0 <= correct_idx < len(options):
            answer = options[correct_idx]
            short_answer = answer[:30] + '...' if len(answer) > 30 else answer
            return format_html(
                '<span style="background:#e8f5e9;color:#2e7d32;padding:4px 10px;border-radius:8px;font-size:12px;">'
                '✓ Option {} : {}</span>',
                obj.correct_option, short_answer
            )
        return "-"
    correct_answer_preview.short_description = "Réponse correcte"

    actions = ['activate_questions', 'deactivate_questions']

    def activate_questions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} question(s) activée(s)")
    activate_questions.short_description = "Activer les questions sélectionnées"

    def deactivate_questions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} question(s) désactivée(s)")
    deactivate_questions.short_description = "Désactiver les questions sélectionnées"


@admin.register(GamePrize)
class GamePrizeAdmin(admin.ModelAdmin):
    """Admin for wheel prizes - CRUD from backoffice."""

    list_display = ['color_preview', 'name', 'prize_type_badge', 'discount_display', 'is_winning_prize', 'applies_to_fresh_products_only', 'order', 'is_active']
    list_filter = ['prize_type', 'is_winning_prize', 'applies_to_fresh_products_only', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']  # Required for autocomplete
    ordering = ['order']

    fieldsets = (
        ('Informations du prix', {
            'fields': ('name', 'prize_type', 'discount_percent', 'description', 'icon'),
            'description': 'Définissez le prix et son type'
        }),
        ('Apparence sur la roue', {
            'fields': ('color', 'order'),
            'description': 'Couleur et position sur la roue (0-7 pour 8 segments)'
        }),
        ('Conditions d\'application', {
            'fields': ('applies_to_fresh_products_only', 'is_winning_prize'),
            'description': 'Décochez "Est un prix gagnant" pour les cases "Pas de chance"'
        }),
        ('Options', {
            'fields': ('is_active',)
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="width:30px;height:30px;background:{};border-radius:4px;border:2px solid #ddd;display:flex;align-items:center;justify-content:center;font-size:16px;">{}</div>',
            obj.color, obj.icon
        )
    color_preview.short_description = "Aperçu"

    def prize_type_badge(self, obj):
        colors = {
            'discount': '#4caf50',
            'free_delivery': '#2196f3',
            'free_item': '#ff9800',
            'lost': '#f44336',
        }
        color = colors.get(obj.prize_type, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_prize_type_display()
        )
    prize_type_badge.short_description = "Type"

    def discount_display(self, obj):
        if obj.prize_type == 'discount' and obj.discount_percent > 0:
            return format_html('<strong style="color:#4caf50;">-{}%</strong>', obj.discount_percent)
        return "-"
    discount_display.short_description = "Réduction"

    actions = ['activate_prizes', 'deactivate_prizes']

    def activate_prizes(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} prix activé(s)")
    activate_prizes.short_description = "Activer les prix sélectionnés"

    def deactivate_prizes(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} prix désactivé(s)")
    deactivate_prizes.short_description = "Désactiver les prix sélectionnés"


@admin.register(GameParticipation)
class GameParticipationAdmin(admin.ModelAdmin):
    """Admin for game participations (quiz + wheel)."""

    list_display = ['name', 'email', 'phone', 'quiz_score_display', 'prize_display', 'promo_code_display', 'promo_status', 'created_at']
    list_filter = ['has_used_prize', 'prize__prize_type', 'prize__is_winning_prize', 'created_at']
    search_fields = ['name', 'email', 'phone', 'promo_code']
    readonly_fields = ['created_at', 'updated_at', 'ip_address']
    ordering = ['-created_at']
    autocomplete_fields = ['prize']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Participant', {
            'fields': ('name', 'email', 'phone', 'ip_address')
        }),
        ('Quiz', {
            'fields': ('quiz_score', 'quiz_total')
        }),
        ('Récompense', {
            'fields': ('prize', 'promo_code', 'has_used_prize'),
            'description': 'Si "Code utilisé" est coché, le code a été utilisé lors d\'une commande'
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def quiz_score_display(self, obj):
        return f"{obj.quiz_score}/{obj.quiz_total}"
    quiz_score_display.short_description = "Score quiz"

    def prize_display(self, obj):
        if obj.prize:
            if obj.prize.is_winning_prize:
                return format_html('<span style="color:green;">{}</span>', obj.prize.name)
            else:
                return format_html('<span style="color:red;">Perdu</span>')
        return "-"
    prize_display.short_description = "Prix"

    def promo_code_display(self, obj):
        if obj.promo_code:
            return format_html(
                '<code style="background:#f5f5f5;padding:3px 8px;border-radius:4px;font-family:monospace;">{}</code>',
                obj.promo_code
            )
        return "-"
    promo_code_display.short_description = "Code promo"

    def promo_status(self, obj):
        if not obj.promo_code:
            return format_html('<span style="color:#999;">-</span>')
        if obj.has_used_prize:
            return format_html(
                '<span style="background:#4caf50;color:white;padding:3px 10px;border-radius:12px;font-size:11px;">✓ Utilisé</span>'
            )
        return format_html(
            '<span style="background:#ff9800;color:white;padding:3px 10px;border-radius:12px;font-size:11px;">En attente</span>'
        )
    promo_status.short_description = "Statut"

    actions = ['mark_as_used', 'mark_as_unused']

    def mark_as_used(self, request, queryset):
        updated = queryset.filter(promo_code__isnull=False).exclude(promo_code='').update(has_used_prize=True)
        self.message_user(request, f"{updated} code(s) promo marqué(s) comme utilisé(s)")
    mark_as_used.short_description = "Marquer les codes comme utilisés"

    def mark_as_unused(self, request, queryset):
        updated = queryset.update(has_used_prize=False)
        self.message_user(request, f"{updated} code(s) promo marqué(s) comme non utilisé(s)")
    mark_as_unused.short_description = "Marquer les codes comme non utilisés"


# ============================================
# OPTIONS DYNAMIQUES POUR DEVIS
# ============================================

@admin.register(FishSpecies)
class FishSpeciesAdmin(admin.ModelAdmin):
    """Admin pour les espèces de poissons."""
    list_display = ['image_preview', 'name', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
    """Admin pour les types de cultures."""
    list_display = ['image_preview', 'name', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(BasinType)
class BasinTypeAdmin(admin.ModelAdmin):
    """Admin pour les types de bassins."""
    list_display = ['image_preview', 'name', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(HydroSystemType)
class HydroSystemTypeAdmin(admin.ModelAdmin):
    """Admin pour les types de systèmes hydroponiques."""
    list_display = ['image_preview', 'name', 'code', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['order', 'name']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(TrainingType)
class TrainingTypeAdmin(admin.ModelAdmin):
    """Admin pour les types de formations."""
    list_display = ['name', 'category', 'duration', 'price_display', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

    def price_display(self, obj):
        if obj.price:
            price_fmt = f"{obj.price:,.0f}".replace(",", " ")
            return f"{price_fmt} FCFA"
        return "-"
    price_display.short_description = "Prix"


# ============================================
# ADMIN SITE CUSTOMIZATION
# ============================================

class AquaRacineAdminSite(AdminSite):
    """Custom admin site with dashboard statistics."""
    site_header = "Aqua-Racine Administration"
    site_title = "Aqua-Racine Admin"
    index_title = "Tableau de bord"

    def index(self, request, extra_context=None):
        """Override index to add dashboard statistics."""
        extra_context = extra_context or {}

        # Calculate date ranges
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Main KPIs
        quote_requests_count = QuoteRequest.objects.count()
        contact_messages_count = ContactMessage.objects.count()
        newsletter_subscribers_count = Newsletter.objects.filter(is_active=True).count()
        products_count = Product.objects.filter(is_active=True).count()

        # Weekly stats
        quotes_this_week = QuoteRequest.objects.filter(created_at__gte=week_ago).count()
        quotes_last_week = QuoteRequest.objects.filter(
            created_at__gte=week_ago - timedelta(days=7),
            created_at__lt=week_ago
        ).count()

        # Calculate percentage for progress bar (max 100%)
        quotes_week_percent = min(quotes_this_week * 10, 100) if quotes_this_week else 0

        # Pending quotes
        pending_quotes = QuoteRequest.objects.filter(status='pending').count()

        # Other counts
        team_members_count = TeamMember.objects.filter(is_active=True).count()
        gallery_images_count = GalleryImage.objects.filter(is_active=True).count()

        # Recent items for dashboard lists
        recent_quotes = QuoteRequest.objects.select_related().prefetch_related('installation_types').order_by('-created_at')[:5]
        recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
        recent_subscribers = Newsletter.objects.filter(is_active=True).order_by('-created_at')[:5]
        recent_game_participations = GameParticipation.objects.select_related('prize').order_by('-created_at')[:5]

        # Build stats dictionary
        extra_context['stats'] = {
            'quote_requests_count': quote_requests_count,
            'contact_messages_count': contact_messages_count,
            'newsletter_subscribers_count': newsletter_subscribers_count,
            'products_count': products_count,
            'quotes_this_week': quotes_this_week,
            'quotes_last_week': quotes_last_week,
            'quotes_week_percent': quotes_week_percent,
            'pending_quotes': pending_quotes,
            'team_members_count': team_members_count,
            'gallery_images_count': gallery_images_count,
        }

        # Recent items
        extra_context['recent_quotes'] = recent_quotes
        extra_context['recent_messages'] = recent_messages
        extra_context['recent_subscribers'] = recent_subscribers
        extra_context['recent_game_participations'] = recent_game_participations

        return super().index(request, extra_context=extra_context)


# Create custom admin site instance
aquaracine_admin_site = AquaRacineAdminSite(name='aquaracine_admin')

# Keep default admin site configuration for fallback
admin.site.site_header = "Aqua-Racine Administration"
admin.site.site_title = "Aqua-Racine Admin"
admin.site.index_title = "Tableau de bord"


def get_dashboard_stats():
    """Helper function to get dashboard statistics for default admin."""
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    return {
        'quote_requests_count': QuoteRequest.objects.count(),
        'contact_messages_count': ContactMessage.objects.count(),
        'newsletter_subscribers_count': Newsletter.objects.filter(is_active=True).count(),
        'products_count': Product.objects.filter(is_active=True).count(),
        'quotes_this_week': QuoteRequest.objects.filter(created_at__gte=week_ago).count(),
        'pending_quotes': QuoteRequest.objects.filter(status='pending').count(),
        'team_members_count': TeamMember.objects.filter(is_active=True).count(),
        'gallery_images_count': GalleryImage.objects.filter(is_active=True).count(),
    }


# Override default admin index
original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    """Override default admin index to include stats."""
    extra_context = extra_context or {}

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Comptages de base
    total_quotes = QuoteRequest.objects.count()
    pending_quotes = QuoteRequest.objects.filter(status='pending').count()
    processed_quotes = QuoteRequest.objects.filter(status='processed').count()
    quotes_this_week = QuoteRequest.objects.filter(created_at__gte=week_ago).count()
    quotes_this_month = QuoteRequest.objects.filter(created_at__gte=month_ago).count()

    # Taux de conversion (devis traités / total)
    conversion_rate = round((processed_quotes / total_quotes * 100), 1) if total_quotes > 0 else 0

    # Messages non lus (on considère les messages récents comme "non lus")
    unread_messages = ContactMessage.objects.filter(created_at__gte=week_ago).count()
    total_messages = ContactMessage.objects.count()

    # Newsletter stats
    total_subscribers = Newsletter.objects.filter(is_active=True).count()
    new_subscribers_week = Newsletter.objects.filter(is_active=True, created_at__gte=week_ago).count()
    new_subscribers_month = Newsletter.objects.filter(is_active=True, created_at__gte=month_ago).count()

    # Devis par type d'installation
    quotes_by_type = []
    try:
        from django.db.models import Count
        quotes_by_type = list(
            QuoteRequest.objects.values('installation_types__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
    except Exception:
        pass

    # Devis par ville/région
    quotes_by_city = []
    try:
        quotes_by_city = list(
            QuoteRequest.objects.exclude(city__isnull=True).exclude(city='')
            .values('city')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
    except Exception:
        pass

    # Données mensuelles pour graphiques (12 derniers mois)
    monthly_quotes = []
    monthly_messages = []
    monthly_labels = []
    for i in range(11, -1, -1):
        month_start = (now - timedelta(days=i*30)).replace(day=1)
        if i > 0:
            month_end = (now - timedelta(days=(i-1)*30)).replace(day=1)
        else:
            month_end = now

        monthly_labels.append(month_start.strftime('%b'))
        monthly_quotes.append(QuoteRequest.objects.filter(
            created_at__gte=month_start, created_at__lt=month_end
        ).count())
        monthly_messages.append(ContactMessage.objects.filter(
            created_at__gte=month_start, created_at__lt=month_end
        ).count())

    # Participations au jeu
    game_participations_count = GameParticipation.objects.count()
    game_winners_count = GameParticipation.objects.filter(prize__is_winning_prize=True).count()

    # Stats complètes
    extra_context['stats'] = {
        # KPIs principaux
        'quote_requests_count': total_quotes,
        'pending_quotes': pending_quotes,
        'processed_quotes': processed_quotes,
        'conversion_rate': conversion_rate,

        # Messages
        'contact_messages_count': total_messages,
        'unread_messages': unread_messages,

        # Newsletter
        'newsletter_subscribers_count': total_subscribers,
        'new_subscribers_week': new_subscribers_week,
        'new_subscribers_month': new_subscribers_month,

        # Tendances
        'quotes_this_week': quotes_this_week,
        'quotes_this_month': quotes_this_month,
        'quotes_week_percent': min(quotes_this_week * 10, 100),

        # Contenu
        'products_count': Product.objects.filter(is_active=True).count(),
        'categories_count': ProductCategory.objects.count() if 'ProductCategory' in dir() else 0,
        'team_members_count': TeamMember.objects.filter(is_active=True).count(),
        'gallery_images_count': GalleryImage.objects.filter(is_active=True).count(),
        'services_count': Service.objects.filter(is_active=True).count(),
        'blog_posts_count': BlogPost.objects.filter(is_published=True).count() if hasattr(BlogPost, 'is_published') else BlogPost.objects.count(),

        # Jeu
        'game_participations_count': game_participations_count,
        'game_winners_count': game_winners_count,

        # Données pour graphiques
        'quotes_by_type': quotes_by_type,
        'quotes_by_city': quotes_by_city,
        'monthly_quotes': monthly_quotes,
        'monthly_messages': monthly_messages,
        'monthly_labels': monthly_labels,
    }

    # Recent items
    extra_context['recent_quotes'] = QuoteRequest.objects.select_related().prefetch_related('installation_types').order_by('-created_at')[:5]
    extra_context['recent_messages'] = ContactMessage.objects.order_by('-created_at')[:5]
    extra_context['recent_subscribers'] = Newsletter.objects.filter(is_active=True).order_by('-created_at')[:5]
    extra_context['recent_game_participations'] = GameParticipation.objects.select_related('prize').order_by('-created_at')[:5]

    return original_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index
