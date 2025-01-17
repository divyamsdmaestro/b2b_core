# Generated by Django 4.2.3 on 2023-12-28 14:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("meta", "0010_alter_city_uuid_alter_country_uuid_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DepartmentCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512, unique=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DepartmentTitle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512, unique=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EmploymentStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512, unique=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="JobDescription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512, unique=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="JobTitle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512, unique=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
