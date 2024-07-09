# Generated by Django 4.2.3 on 2024-01-19 06:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0035_alter_advancedlearningpathresource_custom_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursesubmodule",
            name="evaluation_type",
            field=models.CharField(
                blank=True,
                choices=[("evaluated", "Evaluated"), ("non_evaluated", "Non Evaluated")],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="coursesubmodule",
            name="type",
            field=models.CharField(
                choices=[
                    ("video", "Video"),
                    ("file", "File"),
                    ("custom_url", "Custom URL"),
                    ("scorm", "Scorm"),
                    ("file_submission", "File Submission"),
                ],
                max_length=512,
            ),
        ),
    ]
