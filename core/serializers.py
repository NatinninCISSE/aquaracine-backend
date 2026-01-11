"""
Serializers for Aqua-Racine API.
"""
from rest_framework import serializers
from .models import (
    SiteSettings, HeroSlide, Service, ProductCategory, Product,
    TeamMember, BlogCategory, BlogPost, TimelineStep, GalleryImage,
    Advantage, Testimonial, FAQ, InstallationType, QuoteRequest,
    ContactMessage, Newsletter
)


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for site settings."""

    class Meta:
        model = SiteSettings
        fields = '__all__'


class HeroSlideSerializer(serializers.ModelSerializer):
    """Serializer for hero slides."""

    class Meta:
        model = HeroSlide
        fields = [
            'id', 'title', 'subtitle', 'description', 'image',
            'button_text', 'button_url', 'order', 'is_active'
        ]


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for services."""

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'icon', 'image',
            'order', 'is_active', 'created_at'
        ]


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'order', 'is_active', 'product_count'
        ]

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list (minimal data)."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'description', 'price', 'old_price', 'image',
            'stock', 'unit', 'is_featured', 'is_in_stock'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail (full data)."""
    category = ProductCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'full_description', 'price', 'old_price', 'image',
            'image_2', 'image_3', 'stock', 'unit', 'is_featured',
            'is_active', 'is_in_stock', 'created_at', 'updated_at'
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team members."""

    class Meta:
        model = TeamMember
        fields = [
            'id', 'name', 'role', 'bio', 'photo', 'email',
            'phone', 'linkedin_url', 'facebook_url', 'twitter_url',
            'order', 'is_active'
        ]


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories."""
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(is_published=True).count()


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post list."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'excerpt', 'image', 'author_name', 'author_photo',
            'views', 'is_featured', 'published_date'
        ]


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for blog post detail."""
    category = BlogCategorySerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'excerpt', 'content',
            'image', 'author_name', 'author_photo', 'views',
            'is_featured', 'published_date', 'created_at', 'updated_at'
        ]


class TimelineStepSerializer(serializers.ModelSerializer):
    """Serializer for timeline steps."""

    class Meta:
        model = TimelineStep
        fields = [
            'id', 'title', 'description', 'icon', 'image',
            'video_url', 'order', 'is_active'
        ]


class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery images."""

    class Meta:
        model = GalleryImage
        fields = [
            'id', 'title', 'image', 'category', 'description',
            'order', 'is_active'
        ]


class AdvantageSerializer(serializers.ModelSerializer):
    """Serializer for advantages."""

    class Meta:
        model = Advantage
        fields = [
            'id', 'title', 'description', 'percentage', 'icon',
            'color', 'order', 'is_active'
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials."""

    class Meta:
        model = Testimonial
        fields = [
            'id', 'name', 'role', 'photo', 'content', 'rating',
            'is_active', 'order'
        ]


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQs."""

    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'category', 'order', 'is_active'
        ]


class InstallationTypeSerializer(serializers.ModelSerializer):
    """Serializer for installation types."""

    class Meta:
        model = InstallationType
        fields = [
            'id', 'name', 'description', 'base_price', 'icon',
            'is_active', 'order'
        ]


class QuoteRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating quote requests."""
    installation_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=InstallationType.objects.filter(is_active=True)
    )

    class Meta:
        model = QuoteRequest
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'company',
            'city', 'address', 'installation_types', 'project_size',
            'surface_area', 'budget_range', 'timeline', 'description',
            'has_water_source', 'has_electricity', 'needs_training',
            'needs_maintenance', 'attachment'
        ]

    def create(self, validated_data):
        installation_types = validated_data.pop('installation_types', [])
        quote = QuoteRequest.objects.create(**validated_data)
        quote.installation_types.set(installation_types)
        return quote


class QuoteRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer for quote request details (admin)."""
    installation_types = InstallationTypeSerializer(many=True, read_only=True)

    class Meta:
        model = QuoteRequest
        fields = '__all__'


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact messages."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    """Serializer for contact message details (admin)."""

    class Meta:
        model = ContactMessage
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for newsletter subscriptions."""

    class Meta:
        model = Newsletter
        fields = ['email']

    def create(self, validated_data):
        # Get or create to prevent duplicates
        newsletter, created = Newsletter.objects.get_or_create(
            email=validated_data['email'],
            defaults={'is_active': True}
        )
        if not created and not newsletter.is_active:
            newsletter.is_active = True
            newsletter.save()
        return newsletter


class FullSiteDataSerializer(serializers.Serializer):
    """Serializer for fetching all site data in one request."""
    settings = SiteSettingsSerializer()
    hero_slides = HeroSlideSerializer(many=True)
    services = ServiceSerializer(many=True)
    products = ProductListSerializer(many=True)
    product_categories = ProductCategorySerializer(many=True)
    team_members = TeamMemberSerializer(many=True)
    blog_posts = BlogPostListSerializer(many=True)
    blog_categories = BlogCategorySerializer(many=True)
    timeline_steps = TimelineStepSerializer(many=True)
    gallery_images = GalleryImageSerializer(many=True)
    advantages = AdvantageSerializer(many=True)
    testimonials = TestimonialSerializer(many=True)
    faqs = FAQSerializer(many=True)
    installation_types = InstallationTypeSerializer(many=True)
