# Generated by Django 4.2.3 on 2023-12-14 08:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("meta", "0007_vendor"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0022_alter_courseassessment_type_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Scorm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "upload_status",
                    models.CharField(
                        choices=[
                            ("initiated", "Initiated"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        max_length=512,
                    ),
                ),
                ("file_url", models.URLField(blank=True, default=None, null=True)),
                ("launcher_url", models.URLField(blank=True, default=None, null=True)),
                ("reason", models.TextField(blank=True, default=None, null=True)),
                ("is_standard", models.BooleanField(default=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="modified_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="meta.vendor",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_scorms",
            },
        ),
    ]
