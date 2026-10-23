"""Load the initial catalogue and home-page content. Safe to run repeatedly."""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from shop import data
from shop.models import Category, Product, Review, TeamMember, Testimonial, TrendingImage
from shop.product_copy import COPY, reviews_for

STATIC_IMG = Path(settings.BASE_DIR) / "static" / "img"


def attach_image(upload_to, filename):
    """Copy a static image into MEDIA_ROOT/<upload_to>/ and return its ImageField name."""
    source = STATIC_IMG / Path(filename).name
    target_dir = Path(settings.MEDIA_ROOT) / upload_to
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target_dir / source.name)
    return f"{upload_to}/{source.name}"


class Command(BaseCommand):
    help = "Seed categories, products, trending images, team and testimonial from shop/data.py."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for order, item in enumerate(data.CATEGORIES, start=1):
            categories[item["slug"]], _ = Category.objects.update_or_create(
                slug=item["slug"],
                defaults={"title": item["title"], "nav_title": item["nav"], "display_order": order},
            )

        for item in data.build_products():
            Product.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "category": categories[item["category"]],
                    "price": item["price"],
                    "offer_text": item["offer_text"],
                    "rating": item["rating"],
                    "image": attach_image("products", item["image"]),
                    "display_order": item["display_order"],
                    "is_featured": False,
                    "is_back_to_school": False,
                },
            )

        for flag, items in (("is_featured", data.HOME_FEATURED), ("is_back_to_school", data.HOME_BACK_TO_SCHOOL)):
            for item in items:
                Product.objects.filter(code=item["code"]).update(
                    name=item["name"],
                    image=attach_image("products", item["image"]),
                    **{flag: True},
                )

        for product in Product.objects.all():
            copy = COPY.get(product.name)
            if not copy:
                continue
            product.tagline = copy["tagline"]
            product.description = copy["description"]
            product.key_features = "\n".join(copy["features"])
            product.save(update_fields=["tagline", "description", "key_features"])
            for order, review in enumerate(reviews_for(product.name, copy), start=1):
                Review.objects.update_or_create(
                    product=product,
                    display_order=order,
                    defaults={"title": review["title"], "rating": review["rating"], "comment": review["comment"]},
                )

        for order, path in enumerate(data.HOME_TRENDING, start=1):
            TrendingImage.objects.update_or_create(
                display_order=order,
                defaults={"image": attach_image("trending", path), "caption": "Trending stationery set"},
            )

        for order, member in enumerate(data.TEAM, start=1):
            TeamMember.objects.update_or_create(
                display_order=order,
                defaults={
                    "name": member["name"],
                    "role": member["role"],
                    "photo": attach_image("team", member["image"]),
                },
            )

        testimonial = data.TESTIMONIAL
        Testimonial.objects.update_or_create(
            author_name=testimonial["author_name"],
            defaults={
                "lead_text": testimonial["lead_text"],
                "quote": testimonial["quote"],
                "author_role": testimonial["author_role"],
                "avatar": attach_image("testimonials", testimonial["avatar"]),
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {Category.objects.count()} categories, {Product.objects.count()} products "
            f"({Product.objects.filter(is_featured=True).count()} featured, "
            f"{Product.objects.filter(is_back_to_school=True).count()} back-to-school), "
            f"{TrendingImage.objects.count()} trending images, {TeamMember.objects.count()} team members, "
            f"{Testimonial.objects.count()} testimonials."
        ))
