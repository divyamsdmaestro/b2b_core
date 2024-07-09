# Generated by Django 4.2.3 on 2024-03-14 10:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0042_assignmentgroup_assignmentgroupimagemodel_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="catalogue",
            name="ccms_assignment_group",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.UUIDField(), blank=True, default=None, null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="catalogue",
            name="no_of_assignment_group",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="category",
            name="no_of_assignment_group",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="categoryrole",
            name="no_of_assignment_group",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="categoryskill",
            name="no_of_assignment_group",
            field=models.PositiveIntegerField(default=0),
        ),
    ]