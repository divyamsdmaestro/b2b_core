# Generated by Django 4.2.3 on 2024-03-04 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0039_rename_advanced_learning_path_image_advancedlearningpath_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="skilltraveller",
            name="journey_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("hiking", "Hiking"),
                    ("trekking", "Trekking"),
                    ("weekend_gateway", "Weekend Gateway"),
                    ("business_travel", "Business Travel"),
                    ("event_trip", "Event Trip"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
    ]