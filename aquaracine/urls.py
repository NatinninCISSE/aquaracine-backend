"""
URL configuration for Aqua-Racine project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from core.views import (
    HomePageView, ProductListView, ProductDetailView,
    TeamPageView, BlogListView, BlogDetailView,
    CartPageView, CheckoutPageView, QuoteSuccessView, OrderSuccessView,
    SubmitQuoteView, SubmitContactView, NewsletterSubscribeFormView,
    QuoteFormView, SystemDetailView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Password Reset URLs
    path('admin/password-reset/',
         PasswordResetRequestView.as_view(),
         name='password_reset'),
    path('admin/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='admin/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('admin/password-reset/confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('admin/password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='admin/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # API
    path('api/', include('core.urls')),

    # ========== PAGES ==========
    # Home
    path('', HomePageView.as_view(), name='home'),

    # Products
    path('produits/', ProductListView.as_view(), name='products'),
    path('produit/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    # Team
    path('equipe/', TeamPageView.as_view(), name='team'),

    # Blog
    path('blog/', BlogListView.as_view(), name='blog'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),

    # Cart & Checkout
    path('panier/', CartPageView.as_view(), name='cart'),
    path('paiement/', CheckoutPageView.as_view(), name='checkout'),
    path('commande/succes/', OrderSuccessView.as_view(), name='order_success'),

    # Quote
    path('devis/succes/', QuoteSuccessView.as_view(), name='quote_success'),
    path('devis/envoyer/', SubmitQuoteView.as_view(), name='submit_quote'),
    path('devis/<str:quote_type>/', QuoteFormView.as_view(), name='quote_form'),

    # Systems (Pre-defined models)
    path('systeme/<slug:slug>/', SystemDetailView.as_view(), name='system_detail'),

    # Contact & Newsletter
    path('contact/envoyer/', SubmitContactView.as_view(), name='submit_contact'),
    path('newsletter/inscription/', NewsletterSubscribeFormView.as_view(), name='newsletter_subscribe'),
]

# CKEditor URLs (optionnel)
try:
    from ckeditor_uploader import urls as ckeditor_urls
    urlpatterns.append(path('ckeditor/', include(ckeditor_urls)))
except ImportError:
    pass  # CKEditor not installed

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
