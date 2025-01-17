# Generated by Django 4.2.3 on 2023-11-22 11:55

import apps.common.helpers
import apps.common.model_fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0011_assignment_max_allowed_moduleassignment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("my_learning", "0010_rename_parent_tracker_coursemoduletracker_course_tracker_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubmissionFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "file",
                    apps.common.model_fields.AppFileField(
                        max_length=512, max_size=5, upload_to=apps.common.helpers.file_upload_path
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_submitted_files",
            },
        ),
        migrations.RemoveField(
            model_name="enrollment",
            name="actionee_id",
        ),
        migrations.RemoveField(
            model_name="enrollment",
            name="actionee_name",
        ),
        migrations.AddField(
            model_name="enrollment",
            name="actionee",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="related_enrollment_actionee",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.assignment",
            ),
        ),
        migrations.AddField(
            model_name="userfavourite",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.assignment",
            ),
        ),
        migrations.AddField(
            model_name="userrating",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.assignment",
            ),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="learning_type",
            field=models.CharField(
                choices=[
                    ("course", "Course"),
                    ("learning_path", "Learning Path"),
                    ("advanced_learning_path", "Advanced Learning Path"),
                    ("skill_traveller", "Skill Traveller"),
                    ("playground", "Playground"),
                    ("playground_group", "Playground Group"),
                    ("assignment", "Assignment"),
                ],
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="userfavourite",
            name="favourite_type",
            field=models.CharField(
                choices=[
                    ("course", "Course"),
                    ("learning_path", "Learning Path"),
                    ("advanced_learning_path", "Advanced Learning Path"),
                    ("skill_traveller", "Skill Traveller"),
                    ("playground", "Playground"),
                    ("playground_group", "Playground Group"),
                    ("assignment", "Assignment"),
                    ("category", "Category"),
                    ("skill", "Skill"),
                    ("role", "Role"),
                ],
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="userrating",
            name="learning_type",
            field=models.CharField(
                choices=[
                    ("course", "Course"),
                    ("learning_path", "Learning Path"),
                    ("advanced_learning_path", "Advanced Learning Path"),
                    ("skill_traveller", "Skill Traveller"),
                    ("playground", "Playground"),
                    ("playground_group", "Playground Group"),
                    ("assignment", "Assignment"),
                ],
                max_length=512,
            ),
        ),
        migrations.CreateModel(
            name="AssignmentTracker",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("completed_duration", models.PositiveIntegerField(default=0)),
                (
                    "progress",
                    models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)]),
                ),
                ("is_completed", models.BooleanField(default=False)),
                ("completion_date", models.DateTimeField(blank=True, default=None, null=True)),
                ("last_accessed_on", models.DateTimeField(blank=True, default=None, null=True)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("is_pass", models.BooleanField(blank=True, default=None, null=True)),
                ("start_date", models.DateTimeField(blank=True, default=None, null=True)),
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
                    "enrollment",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="my_learning.enrollment",
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
                    "user",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_assignment_trackers",
            },
        ),
        migrations.CreateModel(
            name="AssignmentSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("feedback", models.TextField(blank=True, default=None, null=True)),
                ("attempt", models.PositiveIntegerField()),
                ("progress", models.FloatField(default=0)),
                ("reattempt_enabled", models.BooleanField(default=False)),
                (
                    "assignment_tracker",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="my_learning.assignmenttracker"),
                ),
                (
                    "evaluator",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("files", models.ManyToManyField(to="my_learning.submissionfile")),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_assignment_submissions",
            },
        ),
    ]
