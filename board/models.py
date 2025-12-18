from django.db import models

from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from decimal import Decimal
User = get_user_model()

PROVINCE_CHOICES = [
    ('ON', 'Ontario'),
    ('QC', 'Quebec'),
    ('BC', 'British Columbia'),
    ('AB', 'Alberta'),
    ('MB', 'Manitoba'),
    ('SK', 'Saskatchewan'),
    ('NS', 'Nova Scotia'),
    ('NB', 'New Brunswick'),
    ('NL', 'Newfoundland and Labrador'),
    ('PE', 'Prince Edward Island'),
    ('NT', 'Northwest Territories'),
    ('YT', 'Yukon'),
    ('NU', 'Nunavut'),
]

CONDITION_CHOICES = [
    ('new', 'New'),
    ('used', 'Used'),
    ('other', 'Other'),
]

LISTING_TYPE_CHOICES = [
    ('offer', 'Offering'),
    ('wanted', 'Wanted'),
    ('exchange', 'Exchange'),
]

LABEL_CHOICES = [
    ('new', 'New'),
    ('urgent', 'Urgent'),
    ('top', 'Top'),
]
SELLER_TYPE_CHOICES = [
    ('individual', 'Seller'),
    ('store', 'Store'),
    ('business', 'Business'),
]

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='subcategories'
    )
    is_visible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CategoryImage(models.Model):
    category = models.ForeignKey(Category, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return f"Image for {self.category.name}"

class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    location = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, blank=True)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, blank=True, null=True)
    latitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,through='Favorite',related_name='favorite_listings',blank=True)
    def __str__(self):
        return self.title
    
class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='listings/')

    def __str__(self):
        return f"Image for {self.listing.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    show_phone = models.BooleanField(default=False)
    show_email = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    seller_type = models.CharField(
        max_length=20,
        choices=SELLER_TYPE_CHOICES,
        default='individual'
    )

    def __str__(self):
        return f'Profile of {self.user.username}'

    def update_rating(self):
        reviews = self.user.received_reviews.all()
        if reviews.exists():
            avg_rating = sum(r.rating for r in reviews) / reviews.count()
            self.rating = round(Decimal(avg_rating), 1)
        else:
            self.rating = Decimal('5.0')
        self.save()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='favorite_entries')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='favorited_by_users')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        unique_together = ('user', 'listing')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} favorited {self.listing.title[:20]}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class ListingReview(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('listing', 'author')  # один отзыв на объявление от одного пользователя

    def __str__(self):
        return f"Review {self.rating}/5 for {self.listing.title} by {self.author.username}"


class ListingComment(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.listing.title}"

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('reviewer', 'seller')  # один отзыв на одного продавца от одного пользователя

    def __str__(self):
        return f"Review {self.rating}/5 for {self.seller.username} by {self.reviewer.username}"

class SiteReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Site Review"
        verbose_name_plural = "Site Reviews"

    def __str__(self):
        return f'{self.user.username} ({self.rating}/5)'

@receiver(post_save, sender=Listing)
def ensure_listingimage_for_listing(sender, instance, created, **kwargs):
    """
    Автоматически создаёт ListingImage,
    если у объявления заполнено поле image,
    но ещё нет связанных images.
    Работает и при создании, и при обновлении.
    """
    if instance.image and not instance.images.exists():
        ListingImage.objects.create(
            listing=instance,
            image=instance.image
        )
