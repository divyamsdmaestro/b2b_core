# Generated by Django 4.2.3 on 2023-12-28 13:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("meta", "0009_mmlconfiguration_alp_yakshaconfiguration_alp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="city",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="country",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="educationtype",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="faculty",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="facultyimagemodel",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="feedbacktemplate",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="feedbacktemplatechoice",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="feedbacktemplatequestion",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="hashtag",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="identificationtype",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="language",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="mmlconfiguration",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="state",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="yakshaconfiguration",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
    ]
