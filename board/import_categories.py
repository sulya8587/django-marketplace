import json
from board.models import Category

def import_categories_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def create_category_tree(entries, parent=None):
        for item in entries:
            category = Category.objects.create(
                name=item['name'],
                slug=item['slug'],
                parent=parent,
                is_visible=True
            )
            if item.get('subcategories'):
                create_category_tree(item['subcategories'], parent=category)

    create_category_tree(data)
