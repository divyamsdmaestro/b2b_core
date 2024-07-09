# Generated by Django 4.2.3 on 2023-11-06 06:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("forum", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("learning", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="forumcourserelationmodel",
            name="course",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.course"),
        ),
        migrations.AddField(
            model_name="forumcourserelationmodel",
            name="forum",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.forum"),
        ),
        migrations.AddField(
            model_name="forum",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="created_by_%(class)s",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="forum",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="deleted_by_%(class)s",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="forum",
            name="forum_image",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="forum.forumimagemodel",
            ),
        ),
        migrations.AddField(
            model_name="forum",
            name="members",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="forum",
            name="modified_by",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="modified_by_%(class)s",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]