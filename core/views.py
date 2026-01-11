"""
Views for Aqua-Racine API and Pages.
"""
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from .models import (
    SiteSettings, HeroSlide, Service, ProductCategory, Product,
    TeamMember, BlogCategory, BlogPost, TimelineStep, GalleryImage,
    Advantage, Testimonial, FAQ, InstallationType, QuoteRequest,
    ContactMessage, Newsletter, SystemModel, Award,
    FishSpecies, CropType, BasinType, HydroSystemType, TrainingType,
    QuizQuestion, GamePrize, GameParticipation
)
import json
import random
import string
from .serializers import (
    SiteSettingsSerializer, HeroSlideSerializer, ServiceSerializer,
    ProductCategorySerializer, ProductListSerializer, ProductDetailSerializer,
    TeamMemberSerializer, BlogCategorySerializer, BlogPostListSerializer,
    BlogPostDetailSerializer, TimelineStepSerializer, GalleryImageSerializer,
    AdvantageSerializer, TestimonialSerializer, FAQSerializer,
    InstallationTypeSerializer, QuoteRequestCreateSerializer,
    QuoteRequestDetailSerializer, ContactMessageCreateSerializer,
    NewsletterSerializer, FullSiteDataSerializer
)


class SiteSettingsView(APIView):
    """Get site settings."""
    permission_classes = [AllowAny]

    def get(self, request):
        settings_obj = SiteSettings.get_settings()
        serializer = SiteSettingsSerializer(settings_obj)
        return Response(serializer.data)


class FullSiteDataView(APIView):
    """
    Get all site data in a single request.
    Useful for initial page load to minimize API calls.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            'settings': SiteSettings.get_settings(),
            'hero_slides': HeroSlide.objects.filter(is_active=True),
            'services': Service.objects.filter(is_active=True),
            'products': Product.objects.filter(is_active=True, is_featured=True)[:8],
            'product_categories': ProductCategory.objects.filter(is_active=True),
            'team_members': TeamMember.objects.filter(is_active=True),
            'blog_posts': BlogPost.objects.filter(is_published=True)[:4],
            'blog_categories': BlogCategory.objects.all(),
            'timeline_steps': TimelineStep.objects.filter(is_active=True),
            'gallery_images': GalleryImage.objects.filter(is_active=True)[:6],
            'advantages': Advantage.objects.filter(is_active=True),
            'testimonials': Testimonial.objects.filter(is_active=True),
            'faqs': FAQ.objects.filter(is_active=True),
            'installation_types': InstallationType.objects.filter(is_active=True),
        }
        serializer = FullSiteDataSerializer(data)
        return Response(serializer.data)


class HeroSlideViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for hero slides."""
    queryset = HeroSlide.objects.filter(is_active=True)
    serializer_class = HeroSlideSerializer
    permission_classes = [AllowAny]


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for services."""
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for product categories."""
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products."""
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_featured', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name', 'order']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products."""
        products = self.queryset.filter(is_featured=True)[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='category/(?P<category_slug>[^/.]+)')
    def by_category(self, request, category_slug=None):
        """Get products by category slug."""
        products = self.queryset.filter(category__slug=category_slug)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class TeamMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for team members."""
    queryset = TeamMember.objects.filter(is_active=True)
    serializer_class = TeamMemberSerializer
    permission_classes = [AllowAny]


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blog categories."""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blog posts."""
    queryset = BlogPost.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_date', 'views', 'title']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured blog posts."""
        posts = self.queryset.filter(is_featured=True)[:4]
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='category/(?P<category_slug>[^/.]+)')
    def by_category(self, request, category_slug=None):
        """Get blog posts by category slug."""
        posts = self.queryset.filter(category__slug=category_slug)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)


class TimelineStepViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for timeline steps."""
    queryset = TimelineStep.objects.filter(is_active=True)
    serializer_class = TimelineStepSerializer
    permission_classes = [AllowAny]


class GalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for gallery images."""
    queryset = GalleryImage.objects.filter(is_active=True)
    serializer_class = GalleryImageSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class AdvantageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for advantages."""
    queryset = Advantage.objects.filter(is_active=True)
    serializer_class = AdvantageSerializer
    permission_classes = [AllowAny]


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for testimonials."""
    queryset = Testimonial.objects.filter(is_active=True)
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for FAQs."""
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class InstallationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for installation types."""
    queryset = InstallationType.objects.filter(is_active=True)
    serializer_class = InstallationTypeSerializer
    permission_classes = [AllowAny]


class QuoteRequestCreateView(generics.CreateAPIView):
    """Create a new quote request."""
    serializer_class = QuoteRequestCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quote = serializer.save()

        # Send confirmation email to client
        try:
            self._send_client_confirmation(quote)
            self._send_admin_notification(quote)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Email sending failed: {e}")

        return Response({
            'success': True,
            'message': 'Votre demande de devis a été envoyée avec succès. Nous vous contacterons sous 48h.',
            'quote_id': quote.pk
        }, status=status.HTTP_201_CREATED)

    def _send_client_confirmation(self, quote):
        """Send confirmation email to the client."""
        subject = f"Aqua-Racine - Confirmation de votre demande de devis #{quote.pk}"
        html_message = render_to_string('emails/quote_confirmation.html', {'quote': quote})
        send_mail(
            subject=subject,
            message=f"Merci {quote.first_name} pour votre demande de devis. Nous vous contacterons sous 48h.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[quote.email],
            html_message=html_message,
            fail_silently=True
        )

    def _send_admin_notification(self, quote):
        """Send notification email to admin."""
        subject = f"Nouvelle demande de devis #{quote.pk} - {quote.full_name}"
        html_message = render_to_string('emails/quote_admin_notification.html', {'quote': quote})
        admin_email = SiteSettings.get_settings().email
        send_mail(
            subject=subject,
            message=f"Nouvelle demande de devis de {quote.full_name} ({quote.email})",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=True
        )


class ContactMessageCreateView(generics.CreateAPIView):
    """Create a new contact message."""
    serializer_class = ContactMessageCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Send notification email
        try:
            self._send_admin_notification(message)
        except Exception as e:
            print(f"Email sending failed: {e}")

        return Response({
            'success': True,
            'message': 'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
        }, status=status.HTTP_201_CREATED)

    def _send_admin_notification(self, message):
        """Send notification email to admin."""
        subject = f"Nouveau message de contact - {message.name}"
        admin_email = SiteSettings.get_settings().email
        send_mail(
            subject=subject,
            message=f"Nouveau message de {message.name} ({message.email}):\n\n{message.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=True
        )


class NewsletterSubscribeView(generics.CreateAPIView):
    """Subscribe to newsletter."""
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': 'Vous êtes maintenant inscrit à notre newsletter.'
        }, status=status.HTTP_201_CREATED)


# =============================================================================
# PAGE VIEWS (Template-based)
# =============================================================================

class BaseContextMixin:
    """Mixin to add common context to all views."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = SiteSettings.get_settings()
        context['installation_types'] = InstallationType.objects.filter(is_active=True)
        return context


class HomePageView(BaseContextMixin, TemplateView):
    """Home page view."""
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_slides'] = HeroSlide.objects.filter(is_active=True)
        context['services'] = Service.objects.filter(is_active=True)
        # Afficher tous les produits actifs (vedettes d'abord, puis les autres)
        context['products'] = Product.objects.filter(is_active=True).order_by('-is_featured', '-created_at')[:8]
        context['team_members'] = TeamMember.objects.filter(is_active=True)[:3]
        context['gallery_images'] = GalleryImage.objects.filter(is_active=True)[:6]
        context['advantages'] = Advantage.objects.filter(is_active=True)[:4]
        context['testimonials'] = Testimonial.objects.filter(is_active=True)
        context['system_models'] = SystemModel.objects.filter(is_active=True)[:6]
        context['awards'] = Award.objects.filter(is_active=True)
        return context


class ProductListView(BaseContextMixin, ListView):
    """Product list page view."""
    model = Product
    template_name = 'pages/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        return context


class ProductDetailView(BaseContextMixin, DetailView):
    """Product detail page view."""
    model = Product
    template_name = 'pages/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class TeamPageView(BaseContextMixin, ListView):
    """Team page view."""
    model = TeamMember
    template_name = 'pages/team.html'
    context_object_name = 'team_members'

    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True)


class BlogListView(BaseContextMixin, ListView):
    """Blog list page view."""
    model = BlogPost
    template_name = 'pages/blog.html'
    context_object_name = 'blog_posts'

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_categories'] = BlogCategory.objects.all()
        context['recent_posts'] = BlogPost.objects.filter(is_published=True)[:5]
        return context


class BlogDetailView(BaseContextMixin, DetailView):
    """Blog detail page view."""
    model = BlogPost
    template_name = 'pages/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj


class CartPageView(BaseContextMixin, TemplateView):
    """Cart page view."""
    template_name = 'pages/cart.html'


class CheckoutPageView(BaseContextMixin, TemplateView):
    """Checkout page view."""
    template_name = 'pages/checkout.html'


class QuoteSuccessView(BaseContextMixin, TemplateView):
    """Quote success page view."""
    template_name = 'pages/quote_success.html'


class OrderSuccessView(BaseContextMixin, TemplateView):
    """Order success page view."""
    template_name = 'pages/order_success.html'


class SubmitQuoteView(View):
    """Handle quote form submission."""

    def post(self, request):
        try:
            # Get installation types
            installation_type_ids = request.POST.getlist('installation_types')

            # Create quote request
            quote = QuoteRequest.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                company=request.POST.get('company', ''),
                city=request.POST.get('city'),
                address=request.POST.get('address', ''),
                project_size=request.POST.get('project_size', 'small'),
                surface_area=request.POST.get('surface_area', ''),
                budget_range=request.POST.get('budget_range', ''),
                description=request.POST.get('description'),
                has_water_source=request.POST.get('has_water_source') == 'on',
                has_electricity=request.POST.get('has_electricity') == 'on',
                needs_training=request.POST.get('needs_training') == 'on',
                needs_maintenance=request.POST.get('needs_maintenance') == 'on',
            )

            # Add installation types
            if installation_type_ids:
                quote.installation_types.set(installation_type_ids)

            # Send emails
            try:
                self._send_client_confirmation(quote)
                self._send_admin_notification(quote)
            except Exception as e:
                print(f"Email sending failed: {e}")

            messages.success(request, 'Votre demande de devis a été envoyée avec succès!')
            return redirect('quote_success')

        except Exception as e:
            messages.error(request, f'Une erreur est survenue: {str(e)}')
            return redirect('home')

    def _send_client_confirmation(self, quote):
        """Send confirmation email to the client."""
        subject = f"Aqua-Racine - Confirmation de votre demande de devis #{quote.pk}"
        html_message = render_to_string('emails/quote_confirmation.html', {'quote': quote})
        send_mail(
            subject=subject,
            message=f"Merci {quote.first_name} pour votre demande de devis.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[quote.email],
            html_message=html_message,
            fail_silently=True
        )

    def _send_admin_notification(self, quote):
        """Send notification email to admin."""
        subject = f"Nouvelle demande de devis #{quote.pk} - {quote.full_name}"
        html_message = render_to_string('emails/quote_admin_notification.html', {'quote': quote})
        admin_email = SiteSettings.get_settings().email
        send_mail(
            subject=subject,
            message=f"Nouvelle demande de devis de {quote.full_name}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=True
        )


class SubmitContactView(View):
    """Handle contact form submission."""

    def post(self, request):
        try:
            message = ContactMessage.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone', ''),
                subject=request.POST.get('subject', 'Message depuis le site'),
                message=request.POST.get('message'),
            )

            # Send notification
            try:
                admin_email = SiteSettings.get_settings().email
                send_mail(
                    subject=f"Nouveau message de contact - {message.name}",
                    message=f"Nouveau message de {message.name} ({message.email}):\n\n{message.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Email sending failed: {e}")

            messages.success(request, 'Votre message a été envoyé avec succès!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Une erreur est survenue: {str(e)}')
            return redirect('home')


class NewsletterSubscribeFormView(View):
    """Handle newsletter subscription form."""

    def post(self, request):
        email = request.POST.get('email')
        if email:
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            if not created and not newsletter.is_active:
                newsletter.is_active = True
                newsletter.save()

            messages.success(request, 'Vous êtes inscrit à notre newsletter!')
        else:
            messages.error(request, 'Veuillez fournir une adresse email valide.')

        return redirect('home')


class QuoteFormView(BaseContextMixin, TemplateView):
    """Quote form page for specific type."""
    template_name = 'pages/quote_form.html'

    QUOTE_TYPES = {
        'pisciculture': {
            'display': 'Pisciculture',
            'icon': 'fa-tint',
            'description': 'Demandez un devis pour votre projet d\'élevage de poissons.',
        },
        'hydroponie': {
            'display': 'Hydroponie',
            'icon': 'fa-leaf',
            'description': 'Demandez un devis pour votre système de culture hors-sol.',
        },
        'aquaponie': {
            'display': 'Aquaponie',
            'icon': 'fa-refresh',
            'description': 'Demandez un devis pour un système combiné poissons et plantes.',
        },
        'formation': {
            'display': 'Formation',
            'icon': 'fa-graduation-cap',
            'description': 'Demandez un devis pour une formation à nos techniques.',
        },
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quote_type = self.kwargs.get('quote_type', 'aquaponie')

        if quote_type not in self.QUOTE_TYPES:
            quote_type = 'aquaponie'

        type_info = self.QUOTE_TYPES[quote_type]
        context['quote_type'] = quote_type
        context['quote_type_display'] = type_info['display']
        context['quote_icon'] = type_info['icon']
        context['quote_description'] = type_info['description']

        # Options dynamiques pour les formulaires
        context['fish_species'] = FishSpecies.objects.filter(is_active=True)
        context['crop_types'] = CropType.objects.filter(is_active=True)
        context['basin_types'] = BasinType.objects.filter(is_active=True)
        context['hydro_system_types'] = HydroSystemType.objects.filter(is_active=True)
        context['training_types'] = TrainingType.objects.filter(is_active=True)

        return context


class SystemDetailView(BaseContextMixin, DetailView):
    """System model detail page view."""
    model = SystemModel
    template_name = 'pages/system_detail.html'
    context_object_name = 'system'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return SystemModel.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related systems (same type, excluding current)
        current = self.object
        context['related_systems'] = SystemModel.objects.filter(
            is_active=True,
            system_type=current.system_type
        ).exclude(pk=current.pk)[:3]
        return context


# ============================================
# GAMIFICATION - QUIZ & WHEEL VIEWS
# ============================================

# Quiz questions pool - varied questions about aquaponics
QUIZ_QUESTIONS = [
    {
        'id': 1,
        'question': "L'aquaponie combine...",
        'options': [
            "L'élevage de poissons et la culture de plantes",
            "L'élevage de poulets et la culture de riz",
            "La pêche en mer et l'agriculture",
            "L'apiculture et le maraîchage"
        ],
        'correct': 0
    },
    {
        'id': 2,
        'question': "Quel pourcentage d'eau économise l'aquaponie par rapport à l'agriculture traditionnelle ?",
        'options': [
            "Environ 30%",
            "Environ 50%",
            "Jusqu'à 90%",
            "Environ 10%"
        ],
        'correct': 2
    },
    {
        'id': 3,
        'question': "Les produits Aqua-Racine sont...",
        'options': [
            "Traités aux pesticides",
            "Importés d'Europe",
            "100% bio et sans pesticides",
            "Génétiquement modifiés"
        ],
        'correct': 2
    },
    {
        'id': 4,
        'question': "Aqua-Racine propose...",
        'options': [
            "Uniquement des poissons",
            "Des systèmes clés en main, formations et produits frais",
            "Uniquement des formations en ligne",
            "Des équipements de pêche"
        ],
        'correct': 1
    },
    {
        'id': 5,
        'question': "En aquaponie, les plantes se nourrissent grâce à...",
        'options': [
            "Des engrais chimiques",
            "L'eau de pluie uniquement",
            "Les déjections des poissons transformées en nutriments",
            "De l'air comprimé"
        ],
        'correct': 2
    },
    {
        'id': 6,
        'question': "Aqua-Racine a été fondée par...",
        'options': [
            "Un groupe d'investisseurs étrangers",
            "Trois jeunes femmes ivoiriennes",
            "Le gouvernement ivoirien",
            "Une université américaine"
        ],
        'correct': 1
    },
    {
        'id': 7,
        'question': "L'aquaponie est considérée comme...",
        'options': [
            "Une technique polluante",
            "Une agriculture non durable",
            "Une solution d'agriculture durable et écologique",
            "Une méthode interdite"
        ],
        'correct': 2
    },
    {
        'id': 8,
        'question': "Quel type de poisson peut-on élever en aquaponie ?",
        'options': [
            "Uniquement des poissons d'eau salée",
            "Des tilapias, silures et autres poissons d'eau douce",
            "Uniquement des poissons d'ornement",
            "Des requins"
        ],
        'correct': 1
    },
    {
        'id': 9,
        'question': "L'hydroponie est...",
        'options': [
            "L'élevage de chevaux",
            "La culture de plantes hors-sol dans l'eau",
            "Une technique de soudure",
            "Un type de massage"
        ],
        'correct': 1
    },
    {
        'id': 10,
        'question': "Aqua-Racine livre ses produits...",
        'options': [
            "Uniquement en Europe",
            "Par voie maritime en 3 mois",
            "Directement à domicile en Côte d'Ivoire",
            "Uniquement au siège de l'entreprise"
        ],
        'correct': 2
    },
    {
        'id': 11,
        'question': "Quels légumes peut-on cultiver en aquaponie ?",
        'options': [
            "Aucun légume",
            "Salades, tomates, herbes aromatiques, etc.",
            "Uniquement des pommes de terre",
            "Uniquement du maïs"
        ],
        'correct': 1
    },
    {
        'id': 12,
        'question': "L'aquaponie utilise...",
        'options': [
            "Beaucoup de pesticides",
            "Des engrais chimiques intensifs",
            "Un cycle naturel sans produits chimiques",
            "De l'eau de mer"
        ],
        'correct': 2
    }
]

# Prizes with probabilities (50% win, 50% lose)
PRIZES = [
    {'code': '10_percent', 'name': '10% de réduction', 'probability': 20},
    {'code': '15_percent', 'name': '15% de réduction', 'probability': 10},
    {'code': 'free_delivery', 'name': 'Livraison gratuite', 'probability': 15},
    {'code': 'free_guide', 'name': 'Guide PDF gratuit', 'probability': 5},
    {'code': 'lost', 'name': 'Pas de chance', 'probability': 50},
]


def generate_promo_code():
    """Generate a unique promo code."""
    prefix = "AQUA"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{suffix}"


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def spin_wheel():
    """Spin the wheel and return a prize from database (alternating win/lose pattern)."""
    # Try to get prizes from database
    db_prizes = list(GamePrize.objects.filter(is_active=True).order_by('order'))

    if db_prizes:
        # Select a random prize
        prize = random.choice(db_prizes)
        return {
            'id': prize.pk,
            'code': prize.prize_type,
            'name': prize.name,
            'discount_percent': prize.discount_percent,
            'is_winning': prize.is_winning_prize,
            'applies_to_fresh_only': prize.applies_to_fresh_products_only,
            'color': prize.color,
            'icon': prize.icon,
        }

    # Fallback to hardcoded prizes
    rand = random.randint(1, 100)
    cumulative = 0
    for prize in PRIZES:
        cumulative += prize['probability']
        if rand <= cumulative:
            return {'code': prize['code'], 'name': prize['name'], 'is_winning': prize['code'] != 'lost'}
    return {'code': 'lost', 'name': 'Pas de chance', 'is_winning': False}


@method_decorator(csrf_exempt, name='dispatch')
class CheckGameEligibility(APIView):
    """Check if user can play the game."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()

        if not email or not phone:
            return Response({
                'eligible': False,
                'message': 'Email et téléphone requis'
            })

        if GameParticipation.has_already_played(email=email, phone=phone):
            return Response({
                'eligible': False,
                'message': 'Vous avez déjà participé au jeu. Une seule participation par personne est autorisée.'
            })

        return Response({
            'eligible': True,
            'message': 'Vous pouvez participer !'
        })


@method_decorator(csrf_exempt, name='dispatch')
class GetQuizQuestions(APIView):
    """Get random quiz questions from database."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # Get active questions from database
        db_questions = list(QuizQuestion.objects.filter(is_active=True))

        # Fallback to hardcoded questions if no questions in DB
        if not db_questions:
            questions = random.sample(QUIZ_QUESTIONS, min(4, len(QUIZ_QUESTIONS)))
            client_questions = []
            for q in questions:
                client_questions.append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': q['options']
                })
            return Response({
                'questions': client_questions,
                'total': len(client_questions)
            })

        # Select 4 random questions from database
        selected = random.sample(db_questions, min(4, len(db_questions)))

        client_questions = []
        for q in selected:
            client_questions.append({
                'id': q.pk,
                'question': q.question,
                'options': q.options
            })

        return Response({
            'questions': client_questions,
            'total': len(client_questions)
        })


@method_decorator(csrf_exempt, name='dispatch')
class SubmitQuizAndSpin(APIView):
    """Submit quiz answers and spin the wheel."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()
        answers = request.data.get('answers', {})  # {question_id: selected_index}

        # Validate inputs
        if not name or not email or not phone:
            return Response({
                'success': False,
                'message': 'Tous les champs sont requis'
            }, status=400)

        # Check if already played
        if GameParticipation.has_already_played(email=email, phone=phone):
            return Response({
                'success': False,
                'message': 'Vous avez déjà participé au jeu.'
            }, status=400)

        # Calculate quiz score - check database first, fallback to hardcoded
        score = 0
        total = 0

        # Try to get questions from database
        db_questions = {str(q.pk): q for q in QuizQuestion.objects.filter(is_active=True)}

        if db_questions:
            # Use database questions
            for q_id, selected_idx in answers.items():
                if q_id in db_questions:
                    total += 1
                    if selected_idx == db_questions[q_id].correct_index:
                        score += 1
        else:
            # Fallback to hardcoded questions
            for q in QUIZ_QUESTIONS:
                q_id = str(q['id'])
                if q_id in answers:
                    total += 1
                    if answers[q_id] == q['correct']:
                        score += 1

        # Spin the wheel
        prize_data = spin_wheel()
        promo_code = ''

        is_winning = prize_data.get('is_winning', prize_data.get('code') != 'lost')
        if is_winning:
            promo_code = generate_promo_code()

        # Get GamePrize instance if available
        prize_instance = None
        if 'id' in prize_data:
            try:
                prize_instance = GamePrize.objects.get(pk=prize_data['id'])
            except GamePrize.DoesNotExist:
                pass

        # Save participation
        participation = GameParticipation.objects.create(
            name=name,
            email=email,
            phone=phone,
            quiz_score=score,
            quiz_total=total if total > 0 else 4,
            prize=prize_instance,
            promo_code=promo_code,
            ip_address=get_client_ip(request)
        )

        # Calculate score message
        quiz_total_final = total if total > 0 else 4
        if score == quiz_total_final:
            score_message = f"Parfait {name} ! Score parfait de {score}/{quiz_total_final} ! 🎉"
        elif score >= quiz_total_final * 0.75:
            score_message = f"Bravo {name} ! Excellent score de {score}/{quiz_total_final} ! 👏"
        elif score >= quiz_total_final * 0.5:
            score_message = f"Bien joué {name} ! Vous avez obtenu {score}/{quiz_total_final}. 👍"
        else:
            score_message = f"Merci {name} ! Vous avez obtenu {score}/{quiz_total_final}. Vous pouvez faire mieux ! 💪"

        return Response({
            'success': True,
            'quiz_score': score,
            'quiz_total': quiz_total_final,
            'score_message': score_message,
            'prize': {
                'code': prize_data.get('code', 'lost'),
                'name': prize_data.get('name', 'Pas de chance'),
                'won': is_winning,
                'discount_percent': prize_data.get('discount_percent', 0),
                'applies_to_fresh_only': prize_data.get('applies_to_fresh_only', True),
            },
            'promo_code': promo_code,
        })


@method_decorator(csrf_exempt, name='dispatch')
class GetWheelSegments(APIView):
    """Get wheel segments from database for display."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # Try to get prizes from database (alternating win/lose)
        db_prizes = list(GamePrize.objects.filter(is_active=True).order_by('order'))

        if db_prizes:
            segments = []
            for prize in db_prizes:
                segments.append({
                    'label': prize.display_name,
                    'color': prize.color,
                    'icon': prize.icon,
                    'prize_type': prize.prize_type,
                    'is_winning': prize.is_winning_prize,
                })
            return Response({'segments': segments, 'total': len(segments)})

        # Fallback to default segments
        default_segments = [
            {'label': '10%', 'color': '#4caf50', 'icon': '🎁', 'prize_type': 'discount', 'is_winning': True},
            {'label': 'Pas de chance', 'color': '#f44336', 'icon': '😔', 'prize_type': 'lost', 'is_winning': False},
            {'label': '15%', 'color': '#2196f3', 'icon': '🎁', 'prize_type': 'discount', 'is_winning': True},
            {'label': 'Pas de chance', 'color': '#ff9800', 'icon': '😔', 'prize_type': 'lost', 'is_winning': False},
            {'label': 'Livraison', 'color': '#9c27b0', 'icon': '🚚', 'prize_type': 'free_delivery', 'is_winning': True},
            {'label': 'Pas de chance', 'color': '#e91e63', 'icon': '😔', 'prize_type': 'lost', 'is_winning': False},
            {'label': '20%', 'color': '#00bcd4', 'icon': '🎁', 'prize_type': 'discount', 'is_winning': True},
            {'label': 'Pas de chance', 'color': '#795548', 'icon': '😔', 'prize_type': 'lost', 'is_winning': False},
        ]
        return Response({'segments': default_segments, 'total': len(default_segments)})


@method_decorator(csrf_exempt, name='dispatch')
class ValidatePromoCode(APIView):
    """Validate a promo code and return discount info."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        code = request.data.get('code', '').strip().upper()

        if not code:
            return Response({
                'valid': False,
                'message': 'Veuillez entrer un code promo'
            })

        # Search for the promo code in GameParticipation
        try:
            participation = GameParticipation.objects.get(
                promo_code__iexact=code,
                has_used_prize=False
            )

            # Check if prize exists and is valid
            if not participation.prize or not participation.prize.is_winning_prize:
                return Response({
                    'valid': False,
                    'message': 'Ce code promo n\'est pas valide'
                })

            prize = participation.prize

            return Response({
                'valid': True,
                'message': f'Code valide ! {prize.name}',
                'discount': {
                    'type': prize.prize_type,
                    'name': prize.name,
                    'percent': prize.discount_percent if prize.prize_type == 'discount' else 0,
                    'free_delivery': prize.prize_type == 'free_delivery',
                    'applies_to_fresh_only': prize.applies_to_fresh_products_only,
                },
                'participation_id': participation.pk,
            })

        except GameParticipation.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'Code promo invalide ou déjà utilisé'
            })


@method_decorator(csrf_exempt, name='dispatch')
class MarkPromoCodeUsed(APIView):
    """Mark a promo code as used after order confirmation."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        code = request.data.get('code', '').strip().upper()

        if not code:
            return Response({'success': False, 'message': 'Code requis'})

        try:
            participation = GameParticipation.objects.get(
                promo_code__iexact=code,
                has_used_prize=False
            )
            participation.has_used_prize = True
            participation.save()

            return Response({
                'success': True,
                'message': 'Code promo marqué comme utilisé'
            })

        except GameParticipation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Code non trouvé ou déjà utilisé'
            })
