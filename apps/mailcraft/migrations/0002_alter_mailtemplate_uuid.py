# Generated by Django 4.2.3 on 2023-12-28 13:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("mailcraft", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mailtemplate",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
    ]
