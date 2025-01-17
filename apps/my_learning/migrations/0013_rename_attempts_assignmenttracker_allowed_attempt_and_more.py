# Generated by Django 4.2.3 on 2023-11-30 13:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("my_learning", "0012_assignmentsubmission_is_pass_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="assignmenttracker",
            old_name="attempts",
            new_name="allowed_attempt",
        ),
        migrations.RemoveField(
            model_name="assignmentsubmission",
            name="reattempt_enabled",
        ),
        migrations.AddField(
            model_name="assignmenttracker",
            name="available_attempt",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="assignmentyakshaschedule",
            name="scheduled_id",
            field=models.IntegerField(),
        ),
    ]
