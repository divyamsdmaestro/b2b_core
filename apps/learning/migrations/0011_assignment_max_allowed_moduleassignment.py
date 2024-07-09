# Generated by Django 4.2.3 on 2023-11-22 11:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0010_rename_resource_courseresource_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="max_allowed",
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name="ModuleAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "assignment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.assignment"),
                ),
                ("module", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.coursemodule")),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_module_assignments",
            },
        ),
    ]
