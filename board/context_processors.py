from .models import Category

def menu_categories(request):
    roots = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    return {
        "menu_categories": roots,     # для верхнего меню (как и было)
        "root_categories": roots,     # добавим это для сайдбара
    }
