# Generated by Django 4.2.3 on 2024-07-02 11:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0019_tenantmasterreport_so_id_tenantmasterreport_so_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantmasterreport",
            name="user_status",
            field=models.BooleanField(default=False),
        ),
    ]