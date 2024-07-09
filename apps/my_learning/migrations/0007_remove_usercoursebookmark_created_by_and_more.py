# Generated by Django 4.2.3 on 2023-11-08 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("my_learning", "0006_rename_alptrackingmodel_useralptracker_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usercoursebookmark",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="usercoursenotes",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="usercoursenotes",
            name="deleted_at",
        ),
        migrations.RemoveField(
            model_name="usercoursenotes",
            name="deleted_by",
        ),
        migrations.RemoveField(
            model_name="usercoursenotes",
            name="is_deleted",
        ),
        migrations.RemoveField(
            model_name="usercoursenotes",
            name="modified_by",
        ),
        migrations.AddField(
            model_name="usercoursebookmark",
            name="user",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="usercoursenotes",
            name="user",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]