from django.contrib import admin
from .models import Listing, Category, CategoryImage
from django.utils.html import format_html

class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [CategoryImageInline]
    list_display = ('name', 'slug', 'is_visible', 'preview_image')
    list_editable = ('is_visible',)
    list_filter = ('is_visible',)
    search_fields = ('name',)
    ordering = ('name',)

    def preview_image(self, obj):
        if obj.images.exists():
            first_image = obj.images.first()
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', first_image.image.url)
        return "-"
    preview_image.short_description = "Image"


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
