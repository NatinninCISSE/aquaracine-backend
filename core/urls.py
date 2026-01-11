"""
URL configuration for Aqua-Racine API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SiteSettingsView, FullSiteDataView,
    HeroSlideViewSet, ServiceViewSet, ProductCategoryViewSet,
    ProductViewSet, TeamMemberViewSet, BlogCategoryViewSet,
    BlogPostViewSet, TimelineStepViewSet, GalleryImageViewSet,
    AdvantageViewSet, TestimonialViewSet, FAQViewSet,
    InstallationTypeViewSet, QuoteRequestCreateView,
    ContactMessageCreateView, NewsletterSubscribeView,
    CheckGameEligibility, GetQuizQuestions, SubmitQuizAndSpin, GetWheelSegments,
    ValidatePromoCode, MarkPromoCodeUsed
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'hero-slides', HeroSlideViewSet, basename='heroslide')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'product-categories', ProductCategoryViewSet, basename='productcategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'team-members', TeamMemberViewSet, basename='teammember')
router.register(r'blog-categories', BlogCategoryViewSet, basename='blogcategory')
router.register(r'blog-posts', BlogPostViewSet, basename='blogpost')
router.register(r'timeline-steps', TimelineStepViewSet, basename='timelinestep')
router.register(r'gallery-images', GalleryImageViewSet, basename='galleryimage')
router.register(r'advantages', AdvantageViewSet, basename='advantage')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')
router.register(r'faqs', FAQViewSet, basename='faq')
router.register(r'installation-types', InstallationTypeViewSet, basename='installationtype')

urlpatterns = [
    # Site data endpoints
    path('settings/', SiteSettingsView.as_view(), name='site-settings'),
    path('site-data/', FullSiteDataView.as_view(), name='full-site-data'),

    # Form submission endpoints
    path('quote-request/', QuoteRequestCreateView.as_view(), name='quote-request'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact-message'),
    path('newsletter/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),

    # Game endpoints (Quiz + Wheel)
    path('game/check-eligibility/', CheckGameEligibility.as_view(), name='game-check-eligibility'),
    path('game/questions/', GetQuizQuestions.as_view(), name='game-questions'),
    path('game/submit/', SubmitQuizAndSpin.as_view(), name='game-submit'),
    path('game/wheel-segments/', GetWheelSegments.as_view(), name='game-wheel-segments'),

    # Promo code endpoints
    path('promo/validate/', ValidatePromoCode.as_view(), name='promo-validate'),
    path('promo/mark-used/', MarkPromoCodeUsed.as_view(), name='promo-mark-used'),

    # Router URLs
    path('', include(router.urls)),
]
