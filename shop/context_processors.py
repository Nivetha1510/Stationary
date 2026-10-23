from . import cart as cart_service
from . import content
from .models import Category


def cart_summary(request):
    """Cart badge + footer/nav data available to every template."""
    return {
        "cart_count": cart_service.count(request),
        "nav_categories": Category.objects.all(),
        "footer_columns": content.FOOTER_COLUMNS,
    }
