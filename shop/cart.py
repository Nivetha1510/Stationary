"""Session-backed shopping cart used by the cart, billing and order pages."""

from decimal import Decimal

from django.conf import settings

from . import content, pricing
from .models import Product

CART_SESSION_KEY = "cart"


def _store(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def add(request, product_id, quantity=1):
    cart = _store(request)
    cart[product_id] = cart.get(product_id, 0) + quantity
    request.session.modified = True


def set_quantity(request, product_id, quantity):
    cart = _store(request)
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity
    request.session.modified = True


def remove(request, product_id):
    cart = _store(request)
    cart.pop(product_id, None)
    request.session.modified = True


def clear(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True


def line_total(unit_price, quantity):
    """Bulk pricing exactly as the cart frame shows: 10+ units cost Rs.249."""
    if quantity >= content.BULK_QTY:
        return Decimal(content.BULK_TOTAL)
    return unit_price * quantity


def items(request):
    """Return cart rows enriched with product data and computed totals."""
    cart = request.session.get(CART_SESSION_KEY, {})
    products = Product.objects.select_related("category").in_bulk(list(cart), field_name="code")
    rows = []
    for code, quantity in cart.items():
        product = products.get(code)
        if not product:
            continue
        rows.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": product.price,
                "total": line_total(product.price, quantity),
                "mrp_total": product.price * quantity,
                "savings": product.price * quantity - line_total(product.price, quantity),
                "bulk_note": f"Buy {content.BULK_QTY} or more @ Rs.{content.BULK_TOTAL}",
            }
        )
    return rows


def totals(request):
    """Bill for the whole cart: bulk savings, taxable value, GST split and grand total."""
    rows = items(request)
    subtotal = sum((row["mrp_total"] for row in rows), Decimal(0))
    taxable = sum((row["total"] for row in rows), Decimal(0))
    bill = pricing.gst_breakup(taxable, settings.GST_RATE)
    bill.update(subtotal=subtotal, discount=subtotal - taxable, taxable=taxable, gstin=settings.SELLER_GSTIN)
    return bill


def count(request):
    return sum(request.session.get(CART_SESSION_KEY, {}).values())
