# Generated by Django 4.2.3 on 2024-06-18 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0018_tenantmasterreport_average_assessment_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantmasterreport",
            name="so_id",
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name="tenantmasterreport",
            name="so_name",
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name="tenantmasterreport",
            name="so_uuid",
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
    ]
