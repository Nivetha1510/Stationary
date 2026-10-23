"""Catalogue, content and order models for the Supplyhive stationery shop."""

import secrets
from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    nav_title = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text='Stable id used by the cart, e.g. "office-1".')
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    offer_text = models.CharField(max_length=150, blank=True)
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    image = models.ImageField(upload_to="products/")
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    key_features = models.TextField(blank=True, help_text="One feature per line.")
    is_featured = models.BooleanField(default=False)
    is_back_to_school = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__display_order", "display_order", "name"]
        verbose_name_plural = "products"

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def offer_line(self):
        return self.offer_text

    @property
    def feature_list(self):
        return [line.strip() for line in self.key_features.splitlines() if line.strip()]

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.code])


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=150)
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name_plural = "reviews"

    def __str__(self):
        return f"{self.product.name}: {self.title}"

    @property
    def stars(self):
        return "\u2605" * self.rating + "\u2606" * (5 - self.rating)


class TrendingImage(models.Model):
    image = models.ImageField(upload_to="trending/")
    caption = models.CharField(max_length=150, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name_plural = "trending images"

    def __str__(self):
        return self.caption or f"Trending image {self.pk}"


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="team/")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name_plural = "team members"

    def __str__(self):
        return f"{self.name} — {self.role}"


class Testimonial(models.Model):
    lead_text = models.CharField(max_length=200)
    quote = models.TextField()
    author_name = models.CharField(max_length=100)
    author_role = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to="testimonials/")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "testimonials"

    def __str__(self):
        return f"{self.author_name} ({self.author_role})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "contact messages"

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "customers"

    def __str__(self):
        return self.user.email


def default_gst_rate():
    return settings.GST_RATE


class Order(models.Model):
    COD, UPI, DEBIT, CREDIT = "cod", "upi", "debit", "credit"
    PAYMENT_CHOICES = [
        (COD, "Cash on Delivery"),
        (UPI, "UPI"),
        (DEBIT, "Debit Card"),
        (CREDIT, "Credit Card"),
    ]

    CONFIRMED, SHIPPED, OUT_FOR_DELIVERY, DELIVERED = (
        "confirmed", "shipped", "out_for_delivery", "delivered",
    )
    STATUS_CHOICES = [
        (CONFIRMED, "Order Confirmed"),
        (SHIPPED, "Shipped"),
        (OUT_FOR_DELIVERY, "Out for Delivery"),
        (DELIVERED, "Delivered"),
    ]
    # how many of the four tracking steps are complete for each status
    _STEPS_DONE = {CONFIRMED: 1, SHIPPED: 2, OUT_FOR_DELIVERY: 3, DELIVERED: 4}
    DELIVERY_DAYS = 4

    PAYMENT_PENDING, PAYMENT_PAID, PAYMENT_FAILED = "pending", "paid", "failed"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_FAILED, "Failed"),
    ]
    PAID = PAYMENT_PAID

    order_code = models.CharField(max_length=11, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    customer_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=200)
    town_city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=COD)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    payment_reference = models.CharField(max_length=20, blank=True, editable=False)
    upi_id = models.CharField(max_length=100, blank=True, editable=False)
    # only the brand and last four digits are ever kept; full numbers and CVVs are discarded
    card_brand = models.CharField(max_length=30, blank=True, editable=False)
    card_last4 = models.CharField(max_length=4, blank=True, editable=False)
    paid_at = models.DateTimeField(null=True, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CONFIRMED)
    # bill breakdown: subtotal - discount = taxable_value; taxable_value + cgst + sgst = total
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    taxable_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=default_gst_rate, editable=False)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name_plural = "orders"

    def __str__(self):
        return f"{self.order_code} — {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self._generate_code()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_code(cls):
        while True:
            code = f"OD{secrets.randbelow(10**9):09d}"
            if not cls.objects.filter(order_code=code).exists():
                return code

    @property
    def is_online_payment(self):
        return self.payment_method != self.COD

    @property
    def payment_label(self):
        if not self.is_online_payment:
            return "Pay on delivery"
        return dict(self.PAYMENT_STATUS_CHOICES)[self.payment_status]

    def bill(self):
        """The bill breakdown for templates."""
        return {
            "subtotal": self.subtotal,
            "discount": self.discount,
            "taxable": self.taxable_value,
            "gst_rate": self.gst_rate,
            "half_rate": self.gst_rate / 2,
            "cgst": self.cgst,
            "sgst": self.sgst,
            "gst": self.cgst + self.sgst,
            "total": self.total,
            "gstin": settings.SELLER_GSTIN,
        }

    def timeline(self):
        """The four tracking steps, with `done` derived from the order status."""
        placed = timezone.localtime(self.created_at) if self.created_at else None
        delivery = placed + timedelta(days=self.DELIVERY_DAYS) if placed else None
        labels = [
            f"Order Confirmed, {placed:%b} {placed.day}" if placed else "Order Confirmed",
            "Shipped",
            "Out for Delivery",
            f"Delivery, {delivery:%b} {delivery.day} by 11 PM" if delivery else "Delivery",
        ]
        done_count = self._STEPS_DONE.get(self.status, 1)
        return [{"label": label, "done": index < done_count} for index, label in enumerate(labels)]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "order items"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def savings(self):
        """Rupees saved by a bulk offer on this line."""
        return self.unit_price * self.quantity - self.line_total

    def save(self, *args, **kwargs):
        if self.line_total is None:
            self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
