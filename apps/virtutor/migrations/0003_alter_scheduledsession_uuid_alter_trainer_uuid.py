# Generated by Django 4.2.3 on 2023-12-28 13:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("virtutor", "0002_scheduledsession_creator_role_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scheduledsession",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="trainer",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
    ]
