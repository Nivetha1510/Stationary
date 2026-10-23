"""Forms for registration, login, contact and billing."""

import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from . import payments
from .models import ContactMessage, Order

User = get_user_model()

PHONE_PATTERN = r"[0-9]{10}"


def normalise_phone(value):
    """Strip spaces/hyphens and require exactly 10 digits."""
    phone = re.sub(r"[\s-]", "", value or "")
    if not re.fullmatch(r"\d{10}", phone):
        raise ValidationError("Enter a 10-digit phone number.")
    return phone


class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs={"placeholder": "Your Name", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email ID", "autocomplete": "email"}),
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "type": "tel", "placeholder": "Phone Number", "pattern": PHONE_PATTERN, "autocomplete": "tel",
            "inputmode": "numeric", "maxlength": "10", "title": "Enter a 10-digit phone number",
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].widget.attrs["maxlength"] = "10"  # the field's own limit would otherwise win

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        return normalise_phone(self.cleaned_data["phone"])

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        data = self.cleaned_data
        with transaction.atomic():
            user = User(username=data["email"], email=data["email"], first_name=data["name"])
            user.set_password(data["password"])
            user.save()
            # the post_save signal has already created the profile
            user.profile.phone = data["phone"]
            user.profile.save(update_fields=["phone"])
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email ID", "autocomplete": "email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "autocomplete": "current-password"}),
    )

    error_message = "Email or password is incorrect."

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").strip().lower()
        password = cleaned.get("password")
        self.user = None
        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise ValidationError(self.error_message)
        return cleaned


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter your Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter Email  ID"}),
            "phone": forms.TextInput(attrs={
                "type": "tel", "placeholder": "Enter your number", "pattern": PHONE_PATTERN,
                "inputmode": "numeric", "maxlength": "10", "title": "Enter a 10-digit phone number",
            }),
            "message": forms.Textarea(attrs={"placeholder": "Enter Message"}),
        }
        labels = {"name": "Name", "email": "Email", "phone": "Phone Number", "message": "Message"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # the layout sizes the textarea with CSS
        for attr in ("rows", "cols"):
            self.fields["message"].widget.attrs.pop(attr, None)
        self.fields["phone"].widget.attrs["maxlength"] = "10"

    def clean_phone(self):
        return normalise_phone(self.cleaned_data["phone"])


class BillingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "street_address", "town_city", "postal_code"]
        widgets = {
            "postal_code": forms.TextInput(attrs={"pattern": "[0-9 ]{6,7}", "inputmode": "numeric"}),
        }
        labels = {
            "customer_name": "Name",
            "street_address": "StreetAddress",
            "town_city": "Town/City",
            "postal_code": "Postal Code",
        }

    def clean_postal_code(self):
        postal = self.cleaned_data["postal_code"].strip()
        if not re.fullmatch(r"\d[\d ]{4,6}\d", postal) or postal.count(" ") > 1 or len(postal.replace(" ", "")) != 6:
            raise ValidationError("Enter a 6-digit postal code (one space allowed).")
        return postal


class UpiIdForm(forms.Form):
    upi_id = forms.CharField(
        max_length=100,
        label="UPI ID",
        widget=forms.TextInput(attrs={
            "placeholder": "name@bank", "autocomplete": "off", "autocapitalize": "none", "spellcheck": "false",
        }),
    )

    def clean_upi_id(self):
        upi_id = self.cleaned_data["upi_id"].strip().lower()
        if not payments.valid_upi_id(upi_id):
            raise ValidationError("Enter a valid UPI ID, like name@bank.")
        return upi_id


class CardPaymentForm(forms.Form):
    card_name = forms.CharField(
        max_length=60,
        label="Name on card",
        widget=forms.TextInput(attrs={"placeholder": "Name on card", "autocomplete": "cc-name"}),
    )
    card_number = forms.CharField(
        max_length=25,
        label="Card number",
        widget=forms.TextInput(attrs={
            "placeholder": "1234 5678 9012 3456", "autocomplete": "cc-number", "inputmode": "numeric",
        }),
    )
    expiry = forms.CharField(
        max_length=7,
        label="Expiry (MM/YY)",
        widget=forms.TextInput(attrs={
            "placeholder": "MM/YY", "autocomplete": "cc-exp", "inputmode": "numeric", "maxlength": "5",
        }),
    )
    cvv = forms.CharField(
        max_length=3,
        label="CVV",
        widget=forms.PasswordInput(attrs={
            "placeholder": "CVV", "autocomplete": "cc-csc", "inputmode": "numeric", "maxlength": "3",
        }),
    )

    def clean_card_name(self):
        name = " ".join(self.cleaned_data["card_name"].split())
        if not re.fullmatch(r"[A-Za-z][A-Za-z .'\-]{1,59}", name):
            raise ValidationError("Enter the name exactly as printed on the card.")
        return name

    def clean_card_number(self):
        number = re.sub(r"[\s-]", "", self.cleaned_data["card_number"])
        # any 16-digit number is accepted (American Express cards have 15); no checksum rule
        expected = 15 if payments.card_brand(number) == "American Express" else 16
        if not number.isdigit() or len(number) != expected:
            raise ValidationError(f"Enter a valid card number ({expected} digits).")
        return number

    def clean_expiry(self):
        match = re.fullmatch(r"(\d{2})\s*/\s*(\d{2})", self.cleaned_data["expiry"].strip())
        if not match:
            raise ValidationError("Enter the expiry as MM/YY.")
        month, year = int(match.group(1)), int(match.group(2))
        if not payments.expiry_valid(month, year):
            raise ValidationError("This card has expired or the expiry date is invalid.")
        return f"{month:02d}/{year:02d}"

    def clean_cvv(self):
        cvv = self.cleaned_data["cvv"].strip()
        if not re.fullmatch(r"\d{3}", cvv):
            raise ValidationError("Enter the 3-digit CVV from your card.")
        return cvv
