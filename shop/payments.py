"""Payment helpers for the on-site UPI and card forms.

DEMO MODE: there is no bank or gateway behind these forms, so a valid form is
accepted as a successful payment (`settings.PAYMENT_DEMO_MODE`). Card numbers and
CVVs are validated and then discarded; only the card brand and last four digits are
saved on the order. To take real money, replace `process_*` with calls to a
PCI-compliant payment gateway (for cards, use the gateway's hosted fields instead of
posting card numbers to this server).
"""

import io
import re
import secrets
from datetime import date
from urllib.parse import quote

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.utils import timezone

UPI_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-_]{1,255}@[a-zA-Z][a-zA-Z0-9]{1,63}$")
# Test card that the demo always declines (so the failure path can be tried).
DECLINE_TEST_CARD = "4000000000000002"


def demo_mode():
    return getattr(settings, "PAYMENT_DEMO_MODE", False)


# ---------------------------------------------------------------- cards

def luhn_valid(number):
    digits = [int(d) for d in number]
    checksum = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def card_brand(number):
    if re.match(r"^3[47]", number):
        return "American Express"
    if re.match(r"^(5[1-5]|2[2-7])", number):
        return "Mastercard"
    if re.match(r"^(60|65|81|82|508)", number):
        return "RuPay"
    if number.startswith("4"):
        return "Visa"
    return ""


def expiry_valid(month, year, today=None):
    """True if MM/YY is a real month that has not passed and is within 20 years."""
    today = today or date.today()
    if not 1 <= month <= 12:
        return False
    full_year = 2000 + year
    if (full_year, month) < (today.year, today.month):
        return False
    return full_year <= today.year + 20


# ------------------------------------------------------------------ UPI

def valid_upi_id(value):
    return bool(UPI_ID_RE.match(value))


def upi_uri(order):
    """The UPI deep link encoded in the QR code (any UPI app can scan or open it)."""
    return (
        f"upi://pay?pa={quote(settings.UPI_MERCHANT_VPA)}&pn={quote(settings.UPI_MERCHANT_NAME)}"
        f"&am={order.total:.2f}&cu=INR&tn={quote('Order ' + order.order_code)}&tr={order.order_code}"
    )


def qr_svg(data):
    """Inline SVG markup for a QR code (generated server-side, safe to embed)."""
    image = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    buffer = io.BytesIO()
    image.save(buffer)
    svg = buffer.getvalue().decode()
    svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
    return re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)


# ---------------------------------------------------------------- orders

def new_reference():
    return "TXN" + "".join(secrets.choice("0123456789") for _ in range(12))


def mark_paid(order, **details):
    """Record a successful payment (idempotent) with whatever non-sensitive details we have."""
    if order.payment_status == order.PAID:
        return False
    order.payment_status = order.PAID
    order.payment_reference = new_reference()
    order.paid_at = timezone.now()
    for field, value in details.items():
        setattr(order, field, value)
    order.save()
    return True
