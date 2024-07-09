# Generated by Django 4.2.3 on 2023-11-06 06:03

import apps.common.helpers
import apps.common.model_fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Forum",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                (
                    "forum_type",
                    models.CharField(
                        choices=[("public", "Public"), ("private", "Private"), ("course", "Course")],
                        default="private",
                        max_length=512,
                    ),
                ),
                ("hashtags", models.TextField(blank=True, default=None, null=True)),
                ("topics", models.TextField(blank=True, default=None, null=True)),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_forums",
            },
        ),
        migrations.CreateModel(
            name="ForumCourseRelationModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "default_related_name": "related_forum_course_relations",
            },
        ),
        migrations.CreateModel(
            name="ForumImageModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    apps.common.model_fields.AppImageField(max_size=5, upload_to=apps.common.helpers.file_upload_path),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "post_type",
                    models.CharField(
                        choices=[("question_based", "Question based"), ("poll_based", "Poll Based")], max_length=512
                    ),
                ),
                ("hashtags", models.TextField(blank=True, default=None, null=True)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("post_attachment", models.URLField(blank=True, default=None, null=True)),
                ("start_date", models.DateField(blank=True, default=None, null=True)),
                ("end_date", models.DateField(blank=True, default=None, null=True)),
                ("enable_end_time", models.BooleanField(default=False)),
                ("enable_hide_discussion", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("forum", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.forum")),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_posts",
            },
        ),
        migrations.CreateModel(
            name="PostComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.post")),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_comments",
            },
        ),
        migrations.CreateModel(
            name="PostImageModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    apps.common.model_fields.AppImageField(max_size=5, upload_to=apps.common.helpers.file_upload_path),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PostPollOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                ("clicked_count", models.IntegerField(default=0)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_poll_options",
            },
        ),
        migrations.CreateModel(
            name="PostReply",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                ("comment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.postcomment")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_replies",
            },
        ),
        migrations.CreateModel(
            name="PostPollOptionClick",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "poll_option",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.postpolloption"),
                ),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.post")),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_poll_options_clicked",
            },
        ),
        migrations.CreateModel(
            name="PostLike",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("is_liked", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="created_by_%(class)s",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="forum.post")),
            ],
            options={
                "abstract": False,
                "default_related_name": "related_likes",
            },
        ),
        migrations.AddField(
            model_name="post",
            name="poll_options",
            field=models.ManyToManyField(blank=True, to="forum.postpolloption"),
        ),
        migrations.AddField(
            model_name="post",
            name="post_image",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="forum.postimagemodel",
            ),
        ),
    ]
