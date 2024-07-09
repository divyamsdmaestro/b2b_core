# Generated by Django 4.2.3 on 2024-04-03 14:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0046_alter_skillontology_options_and_more"),
        ("my_learning", "0030_enrollment_assignment_group_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrollment",
            name="skill_ontology",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.skillontology",
            ),
        ),
        migrations.AddField(
            model_name="userfavourite",
            name="skill_ontology",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.skillontology",
            ),
        ),
        migrations.AddField(
            model_name="userrating",
            name="skill_ontology",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.skillontology",
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
                    ("assignment_group", "Assignment Group"),
                    ("skill_ontology", "Skill Ontology"),
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
                    ("assignment_group", "Assignment Group"),
                    ("category", "Category"),
                    ("skill", "Skill"),
                    ("role", "Role"),
                    ("skill_ontology", "Skill Ontology"),
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
                    ("assignment_group", "Assignment Group"),
                    ("skill_ontology", "Skill Ontology"),
                ],
                max_length=512,
            ),
        ),
        migrations.CreateModel(
            name="UserSkillOntologyTracker",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("last_accessed_on", models.DateTimeField(blank=True, default=None, null=True)),
                ("completed_duration", models.PositiveIntegerField(default=0)),
                (
                    "progress",
                    models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)]),
                ),
                ("is_completed", models.BooleanField(default=False)),
                ("completion_date", models.DateTimeField(blank=True, default=None, null=True)),
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
                    "skill_ontology",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning.skillontology",
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
                "default_related_name": "related_user_skill_ontology_trackers",
            },
        ),
    ]
