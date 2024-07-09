# Generated by Django 4.2.3 on 2024-06-26 07:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("my_learning", "0033_announcementimagemodel_announcement_title_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EnrollmentReminder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
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
                            ("skill_traveller", "Skill Traveller"),
                            ("playground", "Playground"),
                            ("playground_group", "Playground Group"),
                            ("assignment", "Assignment"),
                            ("assignment_group", "Assignment Group"),
                        ],
                        max_length=512,
                        unique=True,
                    ),
                ),
                ("days", models.PositiveIntegerField()),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_enrollment_reminders",
            },
        ),
    ]
