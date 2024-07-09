# Generated by Django 4.2.3 on 2023-11-14 08:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("meta", "0001_initial"),
        ("forum", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="forum",
            name="hashtags",
        ),
        migrations.RemoveField(
            model_name="forum",
            name="topics",
        ),
        migrations.RemoveField(
            model_name="post",
            name="forum",
        ),
        migrations.RemoveField(
            model_name="post",
            name="hashtags",
        ),
        migrations.AddField(
            model_name="forum",
            name="hashtag",
            field=models.ManyToManyField(blank=True, to="meta.hashtag"),
        ),
        migrations.AddField(
            model_name="post",
            name="hashtag",
            field=models.ManyToManyField(blank=True, to="meta.hashtag"),
        ),
        migrations.CreateModel(
            name="ForumTopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                ("forum", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.forum")),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_forum_topics",
            },
        ),
        migrations.AddField(
            model_name="post",
            name="forum_topic",
            field=models.ForeignKey(
                blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to="forum.forumtopic"
            ),
        ),
    ]