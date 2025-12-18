from django.core.management.base import BaseCommand
from board.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Добавляет категории в базу данных'

    def handle(self, *args, **kwargs):
        categories = [
            "Electronics", "Vehicles", "Home & Garden", "Clothing", "Jobs",
            "Services", "Pets", "Real Estate", "Sports Equipment", "Tools & Equipment",
            "Health & Beauty", "Baby Products", "Toys", "Office Supplies",
            "Music & Instruments", "Art & Handcrafts", "Collectibles",
            "Miscellaneous", "Pay & Sell"
        ]

        for name in categories:
            slug = slugify(name)
            category, created = Category.objects.get_or_create(name=name, defaults={'slug': slug})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Добавлена категория: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Категория уже существует: {name}'))
