from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from random import choice
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, HttpResponse
from django.conf import settings
from math import radians, sin, cos, asin, sqrt
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import get_user_model # Оставить
from django import forms # <--- ВОТ ЭТА СТРОКА ДОБАВЛЕНА
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.forms import LoginForm
from .category_icons import CATEGORY_ICONS
from .models import (
    Listing, Category, UserProfile, ListingImage, Favorite,
    ListingReview, ListingComment,  # (ListingReview сейчас не используем, но пусть останется)
    Review, SiteReview,                       # <-- ДОБАВЛЕНО: отзывы о продавце (профиль)
    PROVINCE_CHOICES, LISTING_TYPE_CHOICES, CONDITION_CHOICES, SELLER_TYPE_CHOICES
)

# ФОРМЫ
from .forms import (ListingForm, ListingImageForm, ListingReviewForm, ListingCommentForm,   # (ListingReviewForm можно не использовать)
    ReviewForm, SiteReviewForm,                              # <-- ДОБАВЛЕНО: форма отзыва о продавце (профиль)
)


User = get_user_model()

    
# --- Optional: haversine if you add lat/lon to Listing later ---
def haversine_km(lat1, lon1, lat2, lon2):
    # returns distance in km
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def _get_cookie(request, name, default=None):
    v = request.COOKIES.get(name)
    return v if v is not None and v != '' else default
def set_location(request):
    """
    Save user's location in cookies (city/province and optionally lat/lon), then redirect.
    GET params: city, province, lat, lon, next
    """
    city = request.GET.get('city', '').strip()
    province = request.GET.get('province', '').strip()
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'

    resp = redirect(next_url)
    max_age = 60 * 60 * 24 * 30  # 30 days
    if city:     resp.set_cookie('cu_city', city, max_age=max_age, samesite='Lax')
    if province: resp.set_cookie('cu_province', province, max_age=max_age, samesite='Lax')
    if lat:      resp.set_cookie('cu_lat', lat, max_age=max_age, samesite='Lax')
    if lon:      resp.set_cookie('cu_lon', lon, max_age=max_age, samesite='Lax')
    return resp

def nearby_listings(request):
    """
    Show listings near the user's location.
    MVP: filter by city/province from GET or cookies.
    If lat/lon exist on both user cookies and Listing model -> filter by radius_km.
    """
    # Read from GET first, then cookies
    city = (request.GET.get('city') or _get_cookie(request, 'cu_city', '')).strip()
    province = (request.GET.get('province') or _get_cookie(request, 'cu_province', '')).strip()
    lat = request.GET.get('lat') or _get_cookie(request, 'cu_lat')
    lon = request.GET.get('lon') or _get_cookie(request, 'cu_lon')

    # Optional radius (km); default 50
    try:
        radius_km = float(request.GET.get('radius_km', 50))
    except ValueError:
        radius_km = 50.0

    listings = Listing.objects.all().order_by('-created_at')
    location_label = None
    used_geo_radius = False

    # If you already added Listing.latitude / Listing.longitude (DecimalFields), use geo filter:
    have_geo = lat and lon and hasattr(Listing, 'latitude') and hasattr(Listing, 'longitude')

    if have_geo:
        try:
            ulat, ulon = float(lat), float(lon)
            # naive in-Python distance filter (ok for MVP; for big data use DB/geoindex)
            filtered_ids = []
            for L in listings.only('id', 'latitude', 'longitude'):
                if L.latitude is not None and L.longitude is not None:
                    d = haversine_km(ulat, ulon, float(L.latitude), float(L.longitude))
                    if d <= radius_km:
                        filtered_ids.append(L.id)
            listings = listings.filter(id__in=filtered_ids)
            used_geo_radius = True
            location_label = f"{city}, {province}" if city or province else "your area"
        except Exception:
            # fallback to city/province
            have_geo = False

    if not have_geo:
        if city:
            listings = listings.filter(city__iexact=city)
            location_label = city
            if province:
                listings = listings.filter(province__iexact=province)
                location_label = f"{city}, {province}"
        elif province:
            listings = listings.filter(province__iexact=province)
            location_label = province

    context = {
        'listings': listings,
        'location_label': location_label or 'your area',
        'used_geo_radius': used_geo_radius,
        'radius_km': int(radius_km),
        'city': city,
        'province': province,
    }
    return render(request, 'board/nearby.html', context)
# --- Main Views ---

def index(request):
    query = request.GET.get('q', '')
    selected_category_id = request.GET.get('category')

    # --- location from cookies ---
    city = request.COOKIES.get('cu_city')
    province = request.COOKIES.get('cu_province')

    has_location = bool(city or province)
    location_label = ", ".join(filter(None, [city, province]))

    # --- categories ---
    category_groups = Category.objects.filter(
        is_visible=True,
        parent__isnull=True
    ).prefetch_related('subcategories')

    for cat in category_groups:
        cat.icon = CATEGORY_ICONS.get(cat.name, '📦')

    # --- listings ---
    listings = Listing.objects.all().order_by('-created_at')

    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if selected_category_id:
        listings = listings.filter(category_id=selected_category_id)

    # --- nearby listings (LIMITED) ---
    nearby_listings = Listing.objects.none()

    if has_location:
        nearby_listings = Listing.objects.all()

        if city:
            nearby_listings = nearby_listings.filter(city__iexact=city)
        if province:
            nearby_listings = nearby_listings.filter(province__iexact=province)

        nearby_listings = nearby_listings.order_by('-created_at')[:6]

    context = {
        'category_groups': category_groups,
        'listings': listings,
        'nearby_listings': nearby_listings,
        'has_location': has_location,
        'location_label': location_label,
        'query': query,
        'selected_category_id': int(selected_category_id) if selected_category_id else None,
    }

    return render(request, 'board/index.html', context)


def categories_menu(request):
    return {
        'menu_categories': Category.objects.filter(parent__isnull=True, is_visible=True).prefetch_related('subcategories')
    }


def all_categories_view(request):
    """Список всех категорий."""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').order_by('name')
    for category in categories:
        category.icon = CATEGORY_ICONS.get(category.slug, 'fa-solid fa-tag')
    
    context = {
        'categories': categories,
        'page_title': "All Categories"
    }
    return render(request, 'board/all_categories.html', context)

def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # категория + её непосредственные подкатегории
    subcats = category.subcategories.all()
    cat_ids = [category.id] + list(subcats.values_list('id', flat=True))

    listings = Listing.objects.filter(category_id__in=cat_ids).prefetch_related('images')

    # фильтры
    q = request.GET.get('q', '')
    
    if q:
        listings = listings.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if request.GET.get('location'):
        listings = listings.filter(location__icontains=request.GET['location'])
    if request.GET.get('city'):
        listings = listings.filter(city__icontains=request.GET['city'])
    if request.GET.get('province'):
        listings = listings.filter(province=request.GET['province'])
    if request.GET.get('listing_type'):
        listings = listings.filter(listing_type=request.GET['listing_type'])
    if request.GET.get('condition'):
        listings = listings.filter(condition=request.GET['condition'])

    pr = request.GET.get('price_range')
    if pr:
        try:
            a, b = (pr.split('-') + [''])[:2]
            if a: listings = listings.filter(price__gte=float(a))
            if b: listings = listings.filter(price__lte=float(b))
        except Exception:
            pass

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        listings = listings.order_by('price')
    elif sort == 'price_desc':
        listings = listings.order_by('-price')
    elif sort == 'oldest':
        listings = listings.order_by('created_at')
    else:
        listings = listings.order_by('-created_at')

    all_categories = Category.objects.filter(parent__isnull=True, is_visible=True).order_by('name')
    root_categories = Category.objects.filter(parent__isnull=True, is_visible=True).prefetch_related('subcategories')

    return render(request, 'board/category_detail.html', {
        'category': category,
        'subcategories': subcats,
        'listings': listings,
        'all_categories': all_categories,
        'root_categories': root_categories, 
        'province_choices': PROVINCE_CHOICES if 'PROVINCE_CHOICES' in globals() else [],
        'type_choices': LISTING_TYPE_CHOICES if 'LISTING_TYPE_CHOICES' in globals() else [],
        'condition_choices': CONDITION_CHOICES if 'CONDITION_CHOICES' in globals() else [],
    })

def listing_detail(request, listing_id):
    """Детальная страница объявления."""
    listing = get_object_or_404(Listing.objects.select_related('owner', 'category'), id=listing_id)
    listing.views_count += 1
    listing.save(update_fields=['views_count'])

    images = listing.images.all().order_by('id')
    
    # Отзывы под объявлением
    comment_form = ListingCommentForm()
    comments = ListingComment.objects.filter(listing=listing).select_related('user').order_by('-created_at')

    # Отзыв о самом объявлении (для покупателя)
    review_form = ListingReviewForm()
    reviews = ListingReview.objects.filter(listing=listing).select_related('reviewer').order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    is_favorite = request.user.is_authenticated and listing.favorites.filter(id=request.user.id).exists()
    
    context = {
        'listing': listing,
        'images': images,
        'comment_form': comment_form,
        'comments': comments,
        'is_favorite': is_favorite,
        'review_form': review_form,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'page_title': listing.title
    }

    if request.method == 'POST':
        # Обработка добавления комментария
        if 'add_comment' in request.POST:
            comment_form = ListingCommentForm(request.POST)
            if comment_form.is_valid() and request.user.is_authenticated:
                new_comment = comment_form.save(commit=False)
                new_comment.listing = listing
                new_comment.user = request.user
                new_comment.save()
                messages.success(request, "Your comment was posted.")
                return redirect('listing_detail', listing_id=listing.id)
            elif not request.user.is_authenticated:
                messages.error(request, "You must be logged in to post a comment.")
        
        # Обработка добавления отзыва об объявлении
        elif 'add_review' in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to review this listing.")
                return redirect('listing_detail', listing_id=listing.id)

            review_form = ListingReviewForm(request.POST)
            if review_form.is_valid():
                # Проверка, не оставлял ли пользователь уже отзыв
                if ListingReview.objects.filter(listing=listing, reviewer=request.user).exists():
                    messages.error(request, "You have already submitted a review for this listing.")
                else:
                    new_review = review_form.save(commit=False)
                    new_review.listing = listing
                    new_review.reviewer = request.user
                    new_review.save()
                    messages.success(request, "Your review was successfully added.")
                return redirect('listing_detail', listing_id=listing.id)

    return render(request, 'board/listing_detail.html', context)
def info_page(request):
    return render(request, 'board/about.html')

def contact_page(request):
    return render(request, 'board/contact.html')


@login_required
def create_listing(request):
    ListingImageFormSet = forms.formset_factory(
        ListingImageForm,
        extra=5,
        max_num=5,
        validate_max=True
    )

   
    all_categories = (
        Category.objects
        .filter(parent__isnull=True, is_visible=True)
        .prefetch_related('subcategories')
        .order_by('name')
    )

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        image_formset = ListingImageFormSet(request.POST, request.FILES, prefix='images')

        if form.is_valid() and image_formset.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()

            for image_form in image_formset:
                if image_form.cleaned_data.get('image'):
                    ListingImage.objects.create(
                        listing=listing,
                        image=image_form.cleaned_data['image']
                    )

            messages.success(request, "Listing created successfully.")
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm()
        image_formset = ListingImageFormSet(prefix='images')

    context = {
        'form': form,
        'image_formset': image_formset,
        'all_categories': all_categories,   
        'edit_mode': False,
        'page_title': "Post Your Ad",
    }

    return render(request, 'board/create.html', context)


@login_required
def edit_listing(request, listing_id):
    """Редактирование объявления."""
    listing = get_object_or_404(Listing.objects.select_related('owner'), id=listing_id)
    all_categories = (
    Category.objects
    .filter(parent__isnull=True, is_visible=True)
    .prefetch_related('subcategories')
    .order_by('name')
    )

    if listing.owner != request.user:
        messages.error(request, "You can only edit your own listings.")
        return redirect('listing_detail', listing_id=listing.id)

    ListingImageFormSet = forms.formset_factory(ListingImageForm, extra=5, max_num=5, validate_max=True)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        image_formset = ListingImageFormSet(request.POST, request.FILES, prefix='images')

        if form.is_valid() and image_formset.is_valid():
            listing = form.save()
            
            # Сохранение дополнительных изображений
            for image_form in image_formset:
                if image_form.cleaned_data:
                    ListingImage.objects.create(
                        listing=listing,
                        image=image_form.cleaned_data['image']
                    )
            
            messages.success(request, f"Listing '{listing.title}' updated successfully!")
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm(instance=listing)
        image_formset = ListingImageFormSet(prefix='images')

    current_images = listing.images.all()

    context = {
        'form': form,
        'listing': listing,
        'image_formset': image_formset,
        'current_images': current_images,
        'all_categories': all_categories,   # ✅
        'edit_mode': True,
        'page_title': f"Edit {listing.title}"
    }
    return render(request, 'board/edit_listing.html', context)

@login_required
@require_POST
def delete_listing(request, listing_id):
    """Удаление объявления."""
    listing = get_object_or_404(Listing, id=listing_id)
    if listing.owner != request.user:
        return HttpResponseForbidden("You can delete only your own listings.")
    
    listing.delete()
    messages.success(request, f"Listing '{listing.title}' was deleted.")
    return redirect('my_account')

@login_required
@require_POST
def toggle_favorite(request, listing_id):
    """Добавить/удалить объявление из избранного."""
    listing = get_object_or_404(Listing, id=listing_id)
    
    if listing.favorites.filter(id=request.user.id).exists():
        listing.favorites.remove(request.user)
        messages.info(request, "Removed from favorites.")
    else:
        listing.favorites.add(request.user)
        messages.success(request, "Added to favorites!")
    
    # Возвращаемся на страницу, с которой пришел запрос (если это возможно)
    next_url = request.POST.get('next', request.GET.get('next', None))
    if next_url and url_has_allowed_host_and_scheme(next_url, request.get_host()):
        return redirect(next_url)
    return redirect('listing_detail', listing_id=listing.id)

@login_required
def my_account(request):
    """Личный кабинет: сохраняем seller_type + остальное."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '').strip()
        profile.show_phone = 'show_phone' in request.POST
        profile.show_email = 'show_email' in request.POST
        profile.save()

        messages.success(request, "Contact settings updated.")

        if 'delete_account' in request.POST:
            messages.success(request, "Your account has been deleted.")
            request.user.delete()
            return redirect('index')

        profile.phone = request.POST.get('phone')
        profile.bio = request.POST.get('bio')
        profile.hide_personal_info = 'hide_personal_info' in request.POST

        # сохраняем тип продавца, если пришёл валидный
        seller_type = request.POST.get('seller_type')
        if seller_type in dict(SELLER_TYPE_CHOICES).keys():
            profile.seller_type = seller_type

        if 'remove_avatar' in request.POST:
            profile.avatar.delete(save=False)
            profile.avatar = None

        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']

        profile.save()
        messages.success(request, "Profile updated successfully.")

    favorites = Favorite.objects.filter(user=request.user).select_related('listing').order_by('-added_at')
    saved_listings = [f.listing for f in favorites]
    my_listings = Listing.objects.filter(owner=request.user).order_by('-created_at')

    return render(request, 'board/my_account.html', {
        'profile': profile,
        'saved_listings': saved_listings,
        'my_listings': my_listings,
    })


def search_results(request):
    """Страница результатов поиска."""
    query = request.GET.get('q', '').strip()
    listings_list = Listing.objects.filter(is_active=True).select_related('owner').order_by('-is_promoted', '-created_at')

    if query:
        listings_list = listings_list.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(city__icontains=query)
        ).distinct()
    
    # Пагинация
    paginator = Paginator(listings_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': f"Search results for '{query}'" if query else "Search",
    }
    return render(request, 'board/search_results.html', context)

# --- User Profile & Reviews ---

def user_profile(request, username):
    """Профиль пользователя (продавца) и отзывы о нем."""
    seller = get_object_or_404(User.objects.prefetch_related('listing_set', 'received_reviews'), username=username)
    
    # Объявления пользователя
    listings = seller.listing_set.filter(is_active=True).order_by('-created_at')
    
    # Отзывы о пользователе
    reviews = Review.objects.filter(seller=seller).select_related('reviewer').order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()

    # Форма для отзыва
    review_form = ReviewForm()

    # Проверка, оставлял ли текущий пользователь отзыв
    can_review = False
    if request.user.is_authenticated and request.user != seller:
        if not Review.objects.filter(reviewer=request.user, seller=seller).exists():
            can_review = True

    context = {
        'seller': seller,
        'listings': listings,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'review_count': review_count,
        'review_form': review_form,
        'can_review': can_review,
        'page_title': f"Profile: {seller.get_full_name() or seller.username}"
    }

    if request.method == 'POST' and 'add_review' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect('user_profile', username=username)

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if Review.objects.filter(reviewer=request.user, seller=seller).exists():
                messages.error(request, "You have already reviewed this seller.")
            else:
                review = review_form.save(commit=False)
                review.reviewer = request.user
                review.seller = seller
                review.save()
                messages.success(request, "Your review has been successfully posted.")
        return redirect('user_profile', username=username)

    return render(request, 'board/user_profile.html', context)

@login_required
@require_POST
def delete_user_review(request, username):
    """Удаление отзыва о продавце, оставленного текущим пользователем."""
    seller = get_object_or_404(User, username=username)
    
    # Находим отзыв, оставленный текущим пользователем для этого продавца
    obj = get_object_or_404(Review, seller=seller, reviewer=request.user)
    obj.delete()
    messages.success(request, "Your review was deleted.")
    return redirect('user_profile', username=username)

@login_required
@require_POST
def delete_listing_image(request, listing_id, image_id):
    """Удалить одно фото объявления (и файл на диске)."""
    listing = get_object_or_404(Listing, id=listing_id)
    if listing.owner != request.user:
        return HttpResponseForbidden("You can delete only your own listing photos.")
    img = get_object_or_404(ListingImage, id=image_id, listing=listing)

    if img.image:
        img.image.delete(save=False) 
    img.delete()
    messages.success(request, "Photo removed.")
    return redirect('edit_listing', listing_id=listing.id)

@login_required
@require_POST
def delete_all_listing_images(request, listing_id):
    """Удалить все фото объявления (и файлы на диске)."""
    listing = get_object_or_404(Listing, id=listing_id)
    if listing.owner != request.user:
        return HttpResponseForbidden("You can delete only your own listing photos.")

    images = list(listing.images.all())
    deleted = 0
    for img in images:
        if img.image:
            img.image.delete(save=False)
        img.delete()
        deleted += 1

    if deleted:
        messages.success(request, f"Removed {deleted} photos.")
    else:
        messages.info(request, "No photos to remove.")

    return redirect('edit_listing', listing_id=listing.id)

@login_required
def my_account(request):
    user_listings = Listing.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
    favorite_listings = request.user.favorite_listings.all().select_related('owner').order_by('-created_at')
    my_reviews = Review.objects.filter(reviewer=request.user).select_related('seller').order_by('-created_at')

    context = {
        'user_listings': user_listings,
        'favorite_listings': favorite_listings,
        'my_reviews': my_reviews,
        'page_title': "My Account"
    }
    return render(request, 'board/my_account.html', context)

# --- Comments/Reviews Management ---

@login_required
def edit_comment(request, listing_id, comment_id):
    """Редактирование комментария под объявлением."""
    comment = get_object_or_404(ListingComment, id=comment_id, listing_id=listing_id, user=request.user)

    if request.method == 'POST':
        form = ListingCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect('listing_detail', listing_id=listing_id)
    else:
        form = ListingCommentForm(instance=comment)
    
    context = {
        'form': form,
        'listing_id': listing_id,
        'page_title': "Edit Comment"
    }
    return render(request, 'board/edit_comment.html', context)

@login_required
@require_POST
def delete_comment(request, listing_id, comment_id):
    """Удаление комментария под объявлением."""
    comment = get_object_or_404(ListingComment, id=comment_id, listing_id=listing_id, user=request.user)
    
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect('listing_detail', listing_id=listing_id)

def user_reviews(request):
    """Общие отзывы о сайте."""
    reviews_list = SiteReview.objects.filter().select_related('user').order_by('-created_at')

    # Пагинация
    paginator = Paginator(reviews_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Форма для добавления отзыва
    review_form = SiteReviewForm()

    if request.user.is_authenticated and request.method == 'POST':
        review_form = SiteReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('user_reviews')

    context = {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'review_form': review_form,
        'page_title': "Site Reviews"
    }
    return render(request, 'board/site_reviews.html', context)


# --- Error Handlers (ОБЯЗАТЕЛЬНО ДЛЯ RENDER) ---

def custom_404(request, exception):
    """Кастомный обработчик 404 (Page Not Found)"""
    return render(request, '404.html', {}, status=404)

def custom_500(request):
    """Кастомный обработчик 500 (Server Error)"""
    return render(request, '500.html', {}, status=500)