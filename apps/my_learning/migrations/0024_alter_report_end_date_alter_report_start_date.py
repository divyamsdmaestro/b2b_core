# Generated by Django 4.2.3 on 2024-01-22 06:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("my_learning", "0023_assignmentyakshaschedule_wecp_invite_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="end_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="report",
            name="start_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
