# Generated by Django 4.2.3 on 2023-11-27 10:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0012_catalogue_assignment_catalogue_category_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="forums",
        ),
        migrations.AlterField(
            model_name="coursemodule",
            name="end_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="coursemodule",
            name="start_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
