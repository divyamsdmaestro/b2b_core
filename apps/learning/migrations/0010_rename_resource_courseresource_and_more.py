# Generated by Django 4.2.3 on 2023-11-21 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0009_learningupdateimagemodel_learningupdate"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Resource",
            new_name="CourseResource",
        ),
        migrations.CreateModel(
            name="SkillTravellerResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("video", "Video"),
                            ("audio", "Audio"),
                            ("file", "File"),
                            ("document", "Document"),
                            ("custom_url", "Custom URL"),
                            ("course_within_catalogue", "Course within catalogue"),
                        ],
                        max_length=512,
                    ),
                ),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("file_url", models.URLField(blank=True, default=None, null=True)),
                ("custom_url", models.URLField(blank=True, default=None, null=True)),
                ("duration", models.PositiveIntegerField(blank=True, default=None, null=True)),
                ("is_uploaded", models.BooleanField(blank=True, default=None, null=True)),
                ("is_upload_success", models.BooleanField(blank=True, default=None, null=True)),
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
                    "skill_traveller",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.skilltraveller"),
                ),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_skill_traveller_resources",
            },
        ),
        migrations.CreateModel(
            name="LearningPathResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("video", "Video"),
                            ("audio", "Audio"),
                            ("file", "File"),
                            ("document", "Document"),
                            ("custom_url", "Custom URL"),
                            ("course_within_catalogue", "Course within catalogue"),
                        ],
                        max_length=512,
                    ),
                ),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("file_url", models.URLField(blank=True, default=None, null=True)),
                ("custom_url", models.URLField(blank=True, default=None, null=True)),
                ("duration", models.PositiveIntegerField(blank=True, default=None, null=True)),
                ("is_uploaded", models.BooleanField(blank=True, default=None, null=True)),
                ("is_upload_success", models.BooleanField(blank=True, default=None, null=True)),
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
                    "learning_path",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.learningpath"),
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
            ],
            options={
                "abstract": False,
                "default_related_name": "related_learning_path_resources",
            },
        ),
        migrations.CreateModel(
            name="AssignmentResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("video", "Video"),
                            ("audio", "Audio"),
                            ("file", "File"),
                            ("document", "Document"),
                            ("custom_url", "Custom URL"),
                            ("course_within_catalogue", "Course within catalogue"),
                        ],
                        max_length=512,
                    ),
                ),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("file_url", models.URLField(blank=True, default=None, null=True)),
                ("custom_url", models.URLField(blank=True, default=None, null=True)),
                ("duration", models.PositiveIntegerField(blank=True, default=None, null=True)),
                ("is_uploaded", models.BooleanField(blank=True, default=None, null=True)),
                ("is_upload_success", models.BooleanField(blank=True, default=None, null=True)),
                (
                    "assignment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.assignment"),
                ),
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
            ],
            options={
                "abstract": False,
                "default_related_name": "related_assignment_resources",
            },
        ),
        migrations.CreateModel(
            name="AdvancedLearningPathResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("video", "Video"),
                            ("audio", "Audio"),
                            ("file", "File"),
                            ("document", "Document"),
                            ("custom_url", "Custom URL"),
                            ("course_within_catalogue", "Course within catalogue"),
                        ],
                        max_length=512,
                    ),
                ),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("file_url", models.URLField(blank=True, default=None, null=True)),
                ("custom_url", models.URLField(blank=True, default=None, null=True)),
                ("duration", models.PositiveIntegerField(blank=True, default=None, null=True)),
                ("is_uploaded", models.BooleanField(blank=True, default=None, null=True)),
                ("is_upload_success", models.BooleanField(blank=True, default=None, null=True)),
                (
                    "advanced_learning_path",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.advancedlearningpath"),
                ),
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
            ],
            options={
                "abstract": False,
                "default_related_name": "related_advanced_learning_path_resources",
            },
        ),
    ]
