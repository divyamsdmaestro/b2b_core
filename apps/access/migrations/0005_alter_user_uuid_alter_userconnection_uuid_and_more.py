# Generated by Django 4.2.3 on 2023-12-28 13:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("access", "0004_remove_user_role_user_current_role_user_roles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="userconnection",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="userdetail",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="usereducationdetail",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="userfriendrequest",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="userprofilepicture",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="userskilldetail",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
    ]
