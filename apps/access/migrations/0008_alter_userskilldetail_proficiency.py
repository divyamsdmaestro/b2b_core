# Generated by Django 4.2.3 on 2024-01-08 07:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("access", "0007_alter_userprofilepicture_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userskilldetail",
            name="proficiency",
            field=models.CharField(
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default="basic",
                max_length=512,
            ),
        ),
    ]
