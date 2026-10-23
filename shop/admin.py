from decimal import Decimal

from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html

from . import pricing
from .models import (
    Category,
    ContactMessage,
    Customer,
    Order,
    OrderItem,
    Product,
    Review,
    TeamMember,
    Testimonial,
    TrendingImage,
)

admin.site.site_header = "Supplyhive Administration"
admin.site.site_title = "Supplyhive Admin"
admin.site.index_title = "Catalogue & Orders"


def _thumbnail(image, height=48):
    if not image:
        return "—"
    return format_html('<img src="{}" alt="" style="height:{}px;border-radius:4px;">', image.url, height)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "display_order", "product_count")
    list_editable = ("display_order",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_product_count=Count("products"))

    @admin.display(description="Products", ordering="_product_count")
    def product_count(self, obj):
        return obj._product_count


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ReviewInline]
    list_display = ("thumbnail", "name", "category", "price", "is_featured", "is_back_to_school")
    list_display_links = ("thumbnail", "name")
    list_filter = ("category", "is_featured", "is_back_to_school")
    search_fields = ("name", "code")
    list_editable = ("price", "is_featured", "is_back_to_school")
    list_select_related = ("category",)
    readonly_fields = ("thumbnail", "created_at")

    @admin.display(description="Image")
    def thumbnail(self, obj):
        return _thumbnail(obj.image)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "title", "rating", "display_order")
    list_filter = ("rating",)
    search_fields = ("product__name", "title", "comment")
    list_select_related = ("product",)


@admin.register(TrendingImage)
class TrendingImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "caption", "display_order")
    list_display_links = ("thumbnail", "caption")
    list_editable = ("display_order",)
    readonly_fields = ("thumbnail",)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        return _thumbnail(obj.image)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "role", "display_order")
    list_display_links = ("thumbnail", "name")
    list_editable = ("display_order",)
    search_fields = ("name", "role")
    readonly_fields = ("thumbnail",)

    @admin.display(description="Photo")
    def thumbnail(self, obj):
        return _thumbnail(obj.photo)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_role", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("author_name", "quote")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)
    raw_id_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_code", "customer_name", "user", "town_city", "total", "payment_method", "payment_status",
        "status", "created_at",
    )
    list_filter = ("status", "payment_status", "payment_method", "created_at", "user")
    search_fields = ("order_code", "customer_name")
    date_hierarchy = "created_at"
    readonly_fields = (
        "order_code", "subtotal", "discount", "taxable_value", "gst_rate", "cgst", "sgst", "total",
        "created_at", "payment_reference", "upi_id", "card_brand", "card_last4", "paid_at",
    )
    inlines = [OrderItemInline]
    actions = ["mark_as_shipped", "mark_as_out_for_delivery", "mark_as_delivered"]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        items = list(order.items.all())
        order.subtotal = sum((item.unit_price * item.quantity for item in items), Decimal(0))
        order.taxable_value = sum((item.line_total for item in items), Decimal(0))
        order.discount = order.subtotal - order.taxable_value
        breakup = pricing.gst_breakup(order.taxable_value, order.gst_rate)
        order.cgst, order.sgst, order.total = breakup["cgst"], breakup["sgst"], breakup["total"]
        order.save(update_fields=["subtotal", "taxable_value", "discount", "cgst", "sgst", "total"])

    def _set_status(self, request, queryset, status):
        updated = queryset.update(status=status)
        self.message_user(
            request, f"{updated} order(s) marked as {dict(Order.STATUS_CHOICES)[status]}.", messages.SUCCESS
        )

    @admin.action(description="Mark selected orders as shipped")
    def mark_as_shipped(self, request, queryset):
        self._set_status(request, queryset, Order.SHIPPED)

    @admin.action(description="Mark selected orders as out for delivery")
    def mark_as_out_for_delivery(self, request, queryset):
        self._set_status(request, queryset, Order.OUT_FOR_DELIVERY)

    @admin.action(description="Mark selected orders as delivered")
    def mark_as_delivered(self, request, queryset):
        self._set_status(request, queryset, Order.DELIVERED)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at")
    search_fields = ("user__email", "user__first_name", "phone")
    readonly_fields = ("created_at",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at", "is_handled")
    list_filter = ("is_handled", "created_at")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("name", "email", "phone", "message", "created_at")
    actions = ["mark_as_handled"]

    @admin.action(description="Mark selected messages as handled")
    def mark_as_handled(self, request, queryset):
        updated = queryset.update(is_handled=True)
        self.message_user(request, f"{updated} message(s) marked as handled.", messages.SUCCESS)
