from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import all_categories_view 
from allauth.account import views as allauth_views


urlpatterns = [
    # Главная и категории
    path('', views.index, name='index'),
    path('all-categories/', all_categories_view, name='all_categories'),
    path('categories/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('info/', TemplateView.as_view(template_name='board/info.html'), name='info_page'),
    path('reviews/', views.user_reviews, name='user_reviews'),

    # Создание/управление объявлениями
    path('create/', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:listing_id>/edit/', views.edit_listing, name='edit_listing'),
    path('listing/<int:listing_id>/delete/', views.delete_listing, name='delete_listing'),
    path('listing/<int:listing_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('listing/<int:listing_id>/image/<int:image_id>/delete/',
         views.delete_listing_image, name='delete_listing_image'),
    path('listing/<int:listing_id>/images/delete-all/',
         views.delete_all_listing_images, name='delete_all_listing_images'),


    # Комментарии под объявлениями
    path('listing/<int:listing_id>/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('listing/<int:listing_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Поиск
    path('search/', views.search_results, name='search_results'),

    # Профиль пользователя + отзывы о продавце
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('user/<str:username>/review/delete/', views.delete_user_review, name='delete_user_review'),

    # АУТЕНТИФИКАЦИЯ (Все кастомные пути УДАЛЕНЫ, allauth использует свой 'accounts/')

    # Личный кабинет
    path('my-account/', views.my_account, name='my_account'),
    path('help/', TemplateView.as_view(template_name='board/help.html'), name='help_page'),
    # Near-you pages
    path('nearby/', views.nearby_listings, name='nearby_listings'),
    path('set-location/', views.set_location, name='set_location'),
    path('about/', views.info_page, name='info_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('terms/', TemplateView.as_view(template_name='board/terms.html'), name='terms'),
    path('account/delete/',views.delete_account_confirm,name='delete_account'),

]