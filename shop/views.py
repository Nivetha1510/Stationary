from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from . import cart as cart_service
from . import content
from . import payments
from .forms import BillingForm, CardPaymentForm, ContactForm, LoginForm, RegisterForm, UpiIdForm
from .models import (
    Category,
    ContactMessage,
    Order,
    OrderItem,
    Product,
    TeamMember,
    Testimonial,
    TrendingImage,
)


def _payment_methods():
    return [
        {"value": value, "label": label, "icon": content.PAYMENT_ICONS[value]}
        for value, label in Order.PAYMENT_CHOICES
    ]


# --------------------------------------------------------------- static pages

def home(request):
    return render(
        request,
        "pages/home.html",
        {
            "active": "home",
            "featured": Product.objects.filter(is_featured=True).select_related("category"),
            "back_to_school": Product.objects.filter(is_back_to_school=True).select_related("category"),
            "category_cards": content.HOME_CATEGORY_CARDS,
            "highlights": content.HOME_HIGHLIGHTS,
            "trending": TrendingImage.objects.all(),
            "testimonial": Testimonial.objects.filter(is_active=True).first(),
            "team": TeamMember.objects.all(),
            "team_intro": content.TEAM_INTRO,
        },
    )


def about(request):
    return render(
        request,
        "pages/about.html",
        {"active": "about", "team": TeamMember.objects.all(), "team_intro": content.TEAM_INTRO},
    )


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        contact_message = form.save()
        messages.success(
            request,
            f"Thanks {contact_message.name or 'there'} — your message has been sent. "
            "Our team will get back to you shortly.",
        )
        return redirect(f"{reverse('contact')}#write-us")
    return render(request, "pages/contact.html", {"active": "contact", "form": form})


def _safe_next(request):
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return ""


def signin(request):
    mode = request.POST.get("mode") or request.GET.get("mode") or "login"
    if mode not in ("login", "register"):
        mode = "login"
    login_form = LoginForm(auto_id="l-%s")
    register_form = RegisterForm(auto_id="r-%s")

    if request.method == "POST":
        if mode == "register":
            register_form = RegisterForm(request.POST, auto_id="r-%s")
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
                return redirect(_safe_next(request) or "home")
        else:
            login_form = LoginForm(request.POST, auto_id="l-%s")
            if login_form.is_valid():
                login(request, login_form.user)
                return redirect(_safe_next(request) or "home")

    return render(
        request,
        "pages/signin.html",
        {
            "active": "login",
            "mode": mode,
            "login_form": login_form,
            "register_form": register_form,
            "next": _safe_next(request),
        },
    )


@require_POST
def signout(request):
    logout(request)
    return redirect("home")


# ------------------------------------------------------------ catalogue pages

def _price_filter(request):
    """Selected price-range checkboxes -> (Q filter or None, list for the template)."""
    selected = set(request.GET.getlist("price"))
    condition = Q()
    ranges = []
    last = len(content.PRICE_RANGES) - 1
    for index, (value, label, low, high) in enumerate(content.PRICE_RANGES):
        checked = value in selected
        ranges.append({"value": value, "label": label, "checked": checked})
        if checked:
            upper = Q(price__lte=high) if index == last else Q(price__lt=high)
            condition |= Q(price__gte=low) & upper
    return (condition if selected & {r["value"] for r in ranges} else None), ranges


def _render_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.select_related("category")
    condition, price_ranges = _price_filter(request)
    if condition is not None:
        products = products.filter(condition)
    return render(
        request,
        "pages/category.html",
        {
            "active": "shop",
            "category": category,
            "products": products,
            "result_count": products.count(),
            "price_ranges": price_ranges,
            "price_filtered": condition is not None,
        },
    )


def shop(request):
    return _render_category(request, "office")


def category(request, slug):
    return _render_category(request, slug)


def product_detail(request, code):
    product = get_object_or_404(Product.objects.select_related("category"), code=code)
    return render(
        request,
        "pages/product_detail.html",
        {
            "active": "shop",
            "product": product,
            "features": product.feature_list,
            "reviews": product.reviews.all(),
            "bulk_note": f"Buy pack of {content.BULK_QTY} @ Rs. {content.BULK_TOTAL}",
            "bulk_saving": product.price * content.BULK_QTY - content.BULK_TOTAL,
            "gst_rate": settings.GST_RATE,
        },
    )


def search(request):
    query = request.GET.get("q", "").strip()
    if query:
        matches = Product.objects.filter(name__icontains=query).select_related("category")
    else:
        matches = Product.objects.none()
    return render(
        request,
        "pages/search.html",
        {"active": "shop", "query": query, "products": matches[:12], "result_count": matches.count()},
    )


# ----------------------------------------------------------------- cart flow

def cart_view(request):
    rows = cart_service.items(request)
    bill = cart_service.totals(request)
    return render(
        request,
        "pages/cart.html",
        {"active": "cart", "rows": rows, "bill": bill},
    )


@require_POST
def cart_add(request, product_id):
    get_object_or_404(Product, code=product_id)
    cart_service.add(request, product_id, int(request.POST.get("quantity", 1)))
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"count": cart_service.count(request)})
    messages.success(request, "Added to cart.")
    return redirect(_safe_next(request) or "cart")


@require_POST
def cart_update(request, product_id):
    action = request.POST.get("action")
    current = request.session.get(cart_service.CART_SESSION_KEY, {}).get(product_id, 0)
    if action == "increase":
        quantity = current + 1
    elif action == "decrease":
        quantity = current - 1
    else:
        quantity = int(request.POST.get("quantity", current) or 0)
    cart_service.set_quantity(request, product_id, quantity)
    return redirect("cart")


@require_POST
def cart_remove(request, product_id):
    cart_service.remove(request, product_id)
    return redirect("cart")


def _billing_initial(user):
    initial = {"customer_name": user.first_name}
    last = user.orders.first()
    if last:
        initial.update(
            customer_name=last.customer_name,
            street_address=last.street_address,
            town_city=last.town_city,
            postal_code=last.postal_code,
        )
    return initial


@login_required
def billing(request):
    rows = cart_service.items(request)
    bill = cart_service.totals(request)

    if request.method == "POST":
        if not rows:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")
        form = BillingForm(request.POST)
        if form.is_valid():
            payment = request.POST.get("payment", Order.COD)
            if payment not in dict(Order.PAYMENT_CHOICES):
                payment = Order.COD
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.payment_method = payment
                order.subtotal = bill["subtotal"]
                order.discount = bill["discount"]
                order.taxable_value = bill["taxable"]
                order.gst_rate = bill["gst_rate"]
                order.cgst = bill["cgst"]
                order.sgst = bill["sgst"]
                order.total = bill["total"]
                order.save()
                OrderItem.objects.bulk_create(
                    OrderItem(
                        order=order,
                        product=row["product"],
                        quantity=row["quantity"],
                        unit_price=row["unit_price"],
                        line_total=row["total"],
                    )
                    for row in rows
                )
            request.session["order_id"] = order.pk
            if order.is_online_payment:
                # the cart stays until the payment is confirmed
                return redirect("pay", order_code=order.order_code)
            cart_service.clear(request)
            messages.success(request, "Order placed successfully. Please keep cash ready for delivery.")
            return redirect("my_order")
        selected_payment = request.POST.get("payment", Order.COD)
    else:
        form = BillingForm(initial=_billing_initial(request.user))
        selected_payment = Order.COD

    return render(
        request,
        "pages/billing.html",
        {
            "active": "cart",
            "form": form,
            "rows": rows,
            "bill": bill,
            "payment_methods": _payment_methods(),
            "selected_payment": selected_payment,
        },
    )


def _current_order(request):
    """One of the signed-in user's own orders, or None.

    The session `order_id` only picks which of the user's orders to show; it can
    never reach another customer's order.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
    order = orders.filter(pk=request.session.get("order_id")).first() or orders.first()
    if not order:
        return None
    return {
        "code": order.order_code,
        "name": order.customer_name,
        "street": order.street_address,
        "city": order.town_city,
        "postal": order.postal_code,
        "payment": order.payment_method,
        "total": order.total,
        "bill": order.bill(),
        "payment_label": order.payment_label,
        "pay_url": (
            reverse("pay", args=[order.order_code])
            if order.is_online_payment and order.payment_status != order.PAID
            else ""
        ),
        "lines": [
            {
                "name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total": item.line_total,
                "image_url": item.product.image.url,
            }
            for item in order.items.all()
        ],
        "steps": order.timeline(),
    }


@login_required
def my_order(request):
    return render(
        request,
        "pages/my_order.html",
        {"active": "orders", "order": _current_order(request)},
    )


@login_required
def tracking(request):
    order = _current_order(request)
    return render(
        request,
        "pages/tracking.html",
        {
            "active": "orders",
            "order": order,
            "steps": order["steps"] if order else [],
            "payment_methods": _payment_methods(),
        },
    )


# ------------------------------------------------------------------ payments

def _own_order(request, order_code):
    return get_object_or_404(Order, order_code=order_code, user=request.user)


def _finish_payment(request, order):
    cart_service.clear(request)
    request.session["order_id"] = order.pk
    messages.success(request, f"Payment successful! Your order is confirmed. Reference: {order.payment_reference}")
    return redirect("my_order")


@login_required
@never_cache
def pay(request, order_code):
    order = _own_order(request, order_code)
    if not order.is_online_payment or order.payment_status == order.PAID:
        return redirect("my_order")
    if not payments.demo_mode():
        messages.error(request, "Online payments are not available right now. Please choose Cash on Delivery.")
        return redirect("billing")

    is_upi = order.payment_method == Order.UPI
    mode = request.POST.get("mode") or request.GET.get("mode") or ("qr" if is_upi else "card")
    if is_upi and mode not in ("qr", "upi_id"):
        mode = "qr"
    upi_form = UpiIdForm()
    card_form = CardPaymentForm()

    if request.method == "POST":
        if is_upi and mode == "qr":
            # the customer confirms they paid by scanning the QR code
            payments.mark_paid(order)
            return _finish_payment(request, order)
        if is_upi:
            upi_form = UpiIdForm(request.POST)
            if upi_form.is_valid():
                payments.mark_paid(order, upi_id=upi_form.cleaned_data["upi_id"])
                return _finish_payment(request, order)
        else:
            card_form = CardPaymentForm(request.POST)
            if card_form.is_valid():
                number = card_form.cleaned_data["card_number"]
                if number == payments.DECLINE_TEST_CARD:
                    card_form.add_error(None, "Your card was declined by the bank. Please try another card.")
                else:
                    payments.mark_paid(
                        order, card_brand=payments.card_brand(number), card_last4=number[-4:]
                    )
                    return _finish_payment(request, order)

    uri = payments.upi_uri(order) if is_upi else ""
    return render(
        request,
        "pages/pay.html",
        {
            "active": "cart",
            "order": order,
            "is_upi": is_upi,
            "mode": mode,
            "method_label": order.get_payment_method_display(),
            "upi_form": upi_form,
            "card_form": card_form,
            "qr_svg": payments.qr_svg(uri) if is_upi else "",
            "upi_uri": uri,
        },
    )
