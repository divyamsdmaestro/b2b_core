# Generated by Django 4.2.3 on 2024-05-06 13:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0047_alter_skilltraveller_journey_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="assignment",
            name="author",
        ),
        migrations.AddField(
            model_name="assignment",
            name="author",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
