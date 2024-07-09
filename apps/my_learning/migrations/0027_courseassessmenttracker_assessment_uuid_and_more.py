# Generated by Django 4.2.3 on 2024-02-28 14:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("my_learning", "0026_rename_course_assessment_courseassessmenttracker_assessment_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="courseassessmenttracker",
            name="assessment_uuid",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="courseassessmenttracker",
            name="reattempt_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lpassessmenttracker",
            name="assessment_uuid",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="lpassessmenttracker",
            name="reattempt_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]