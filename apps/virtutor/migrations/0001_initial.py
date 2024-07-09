# Generated by Django 4.2.3 on 2023-11-06 06:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Trainer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=512)),
                ("last_name", models.CharField(max_length=512)),
                ("trainer_id", models.IntegerField()),
                ("skills", models.JSONField()),
                ("alp", models.ManyToManyField(blank=True, to="learning.advancedlearningpath")),
                ("course", models.ManyToManyField(blank=True, to="learning.course")),
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
                ("learning_path", models.ManyToManyField(blank=True, to="learning.learningpath")),
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
            ],
            options={
                "default_related_name": "related_trainers",
            },
        ),
        migrations.CreateModel(
            name="ScheduledSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("session_title", models.CharField(max_length=512)),
                ("session_code", models.CharField(max_length=512)),
                ("scheduled_id", models.IntegerField()),
                ("session_url", models.URLField()),
                ("external_session_url", models.URLField()),
                ("base_url", models.URLField()),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
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
                ("module", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.coursemodule")),
            ],
            options={
                "default_related_name": "related_scheduled_sessions",
            },
        ),
    ]
