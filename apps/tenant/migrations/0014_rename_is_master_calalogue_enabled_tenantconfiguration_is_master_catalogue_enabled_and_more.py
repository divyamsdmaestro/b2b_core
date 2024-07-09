# Generated by Django 4.2.3 on 2024-03-28 13:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0013_tenantconfiguration_is_assignment_enabled_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tenantconfiguration",
            old_name="is_master_calalogue_enabled",
            new_name="is_master_catalogue_enabled",
        ),
        migrations.AddField(
            model_name="tenantconfiguration",
            name="is_skill_ontology_enabled",
            field=models.BooleanField(default=False),
        ),
    ]
