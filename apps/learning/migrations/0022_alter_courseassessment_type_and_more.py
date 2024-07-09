# Generated by Django 4.2.3 on 2023-12-13 11:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0021_courseassessment_is_practice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courseassessment",
            name="type",
            field=models.CharField(
                choices=[("dependent_assessment", "Dependent Assessment"), ("final_assessment", "Final Assessment")],
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="courseassignment",
            name="type",
            field=models.CharField(
                choices=[("dependent_assignment", "Dependent Assignment"), ("final_assignment", "Final Assignment")],
                max_length=512,
            ),
        ),
        migrations.CreateModel(
            name="LPAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("sequence", models.PositiveIntegerField(default=0)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("dependent_assignment", "Dependent Assignment"),
                            ("final_assignment", "Final Assignment"),
                        ],
                        max_length=512,
                    ),
                ),
                (
                    "assignment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.assignment"),
                ),
                (
                    "learning_path",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="learning.learningpath",
                    ),
                ),
                (
                    "lp_course",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="learning.learningpathcourse",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_lp_assignments",
            },
        ),
        migrations.CreateModel(
            name="LPAssessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("sequence", models.PositiveIntegerField(default=0)),
                ("name", models.CharField(blank=True, default=None, max_length=512, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("dependent_assessment", "Dependent Assessment"),
                            ("final_assessment", "Final Assessment"),
                        ],
                        max_length=512,
                    ),
                ),
                ("yaksha_uuid", models.UUIDField()),
                ("is_practice", models.BooleanField(default=False)),
                (
                    "learning_path",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="learning.learningpath",
                    ),
                ),
                (
                    "lp_course",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="learning.learningpathcourse",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_lp_assessments",
            },
        ),
    ]
