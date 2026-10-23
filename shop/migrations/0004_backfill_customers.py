from django.conf import settings
from django.db import migrations


def create_missing_customers(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Customer = apps.get_model("shop", "Customer")
    for user in User.objects.filter(profile__isnull=True):
        Customer.objects.create(user=user)


class Migration(migrations.Migration):
    dependencies = [("shop", "0003_customer_and_order_user")]

    operations = [migrations.RunPython(create_missing_customers, migrations.RunPython.noop)]
