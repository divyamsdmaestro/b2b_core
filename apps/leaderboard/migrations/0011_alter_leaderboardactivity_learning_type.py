# Generated by Django 4.2.3 on 2024-03-14 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leaderboard", "0010_leaderboardactivity_ccms_data_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leaderboardactivity",
            name="learning_type",
            field=models.CharField(
                blank=True,
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
                default=None,
                max_length=512,
                null=True,
            ),
        ),
    ]