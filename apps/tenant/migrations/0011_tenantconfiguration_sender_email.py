# Generated by Django 4.2.3 on 2024-01-25 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0010_tenantconfiguration_is_wecp_enabled_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantconfiguration",
            name="sender_email",
            field=models.EmailField(blank=True, default=None, max_length=254, null=True),
        ),
    ]