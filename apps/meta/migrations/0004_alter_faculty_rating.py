# Generated by Django 4.2.3 on 2023-12-05 09:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meta", "0003_rename_attempt_yakshaconfiguration_allowed_attempts_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="faculty",
            name="rating",
            field=models.FloatField(
                blank=True,
                default=None,
                null=True,
                validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)],
            ),
        ),
    ]
