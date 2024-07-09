# Generated by Django 4.2.3 on 2023-11-06 08:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0002_userfavourite"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("access_control", "0001_initial"),
        ("my_learning", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "learning_type",
                    models.CharField(
                        choices=[
                            ("course", "Course"),
                            ("learning_path", "Learning Path"),
                            ("advanced_learning_path", "Advanced Learning Path"),
                            ("sub_skill", "Sub Skill"),
                            ("sub_role", "Sub Role"),
                            ("skill_traveller", "Skill Traveller"),
                            ("playground", "Playground"),
                            ("playground_group", "Playground Group"),
                        ],
                        max_length=512,
                    ),
                ),
                ("actionee_id", models.PositiveIntegerField(blank=True, default=None, null=True)),
                ("actionee_name", models.CharField(blank=True, default=None, max_length=512, null=True)),
                ("reason", models.TextField(blank=True, default=None, null=True)),
                ("action_date", models.DateField(blank=True, default=None, null=True)),
                (
                    "action",
                    models.CharField(
                        choices=[("approved", "Approved"), ("rejected", "Rejected"), ("pending", "Pending")],
                        default="pending",
                        max_length=512,
                    ),
                ),
                (
                    "approval_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("super_admin", "Super Admin"),
                            ("tenant_admin", "Tenant Admin"),
                            ("self_enrolled", "Self Enrolled"),
                        ],
                        default=None,
                        max_length=512,
                        null=True,
                    ),
                ),
                ("start_date", models.DateField(blank=True, default=None, null=True)),
                ("end_date", models.DateField(blank=True, default=None, null=True)),
                (
                    "advanced_learning_path",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.advancedlearningpath",
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.course",
                    ),
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
                    "learning_path",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.learningpath",
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
                    "playground",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.playground",
                    ),
                ),
                (
                    "playground_group",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.playgroundgroup",
                    ),
                ),
                (
                    "skill_traveller",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.skilltraveller",
                    ),
                ),
                (
                    "sub_role",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.subrole",
                    ),
                ),
                (
                    "sub_skill",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.subskill",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_group",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="access_control.usergroup",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_enrollments",
            },
        ),
    ]