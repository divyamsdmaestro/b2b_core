# Generated by Django 4.2.3 on 2024-05-30 12:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0015_tenant_allowed_login_domain_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="api_secret_key",
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
    ]
