from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("category/<slug:slug>/", views.category, name="category"),
    path("product/<str:code>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.signin, name="signin"),
    path("logout/", views.signout, name="signout"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<str:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<str:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<str:product_id>/", views.cart_remove, name="cart_remove"),
    path("billing/", views.billing, name="billing"),
    path("pay/<str:order_code>/", views.pay, name="pay"),
    path("orders/", views.my_order, name="my_order"),
    path("tracking/", views.tracking, name="tracking"),
    path("search/", views.search, name="search"),
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
