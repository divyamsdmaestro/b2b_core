# Generated by Django 4.2.3 on 2023-11-06 06:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenant", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DatabaseRouter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("database_name", models.CharField(max_length=512, unique=True)),
                ("database_user", models.CharField(max_length=512)),
                ("database_password", models.CharField(max_length=512)),
                ("database_host", models.CharField(max_length=512)),
                ("database_port", models.CharField(max_length=512)),
                ("is_default", models.BooleanField(default=False)),
                ("tenant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="tenant.tenant")),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_db_router",
            },
        ),
    ]