# Generated by Django 4.2.3 on 2023-12-20 13:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0025_advancedlearningpath_feedback_template_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="advancedlearningpathresource",
            name="custom_url",
            field=models.URLField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="assignmentresource",
            name="custom_url",
            field=models.URLField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="courseresource",
            name="custom_url",
            field=models.URLField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="coursesubmodule",
            name="custom_url",
            field=models.URLField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="learningpathresource",
            name="custom_url",
            field=models.URLField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="skilltravellerresource",
            name="custom_url",
            field=models.URLField(blank=True, default=None, max_length=512, null=True),
        ),
    ]
