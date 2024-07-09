# Generated by Django 4.2.3 on 2024-03-01 12:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("access_control", "0004_alter_policy_uuid_alter_policycategory_uuid_and_more"),
        ("learning", "0039_rename_advanced_learning_path_image_advancedlearningpath_image_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("my_learning", "0027_courseassessmenttracker_assessment_uuid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignmenttracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="assignmenttracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="courseassessmenttracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="courseassessmenttracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="coursemoduletracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="coursemoduletracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="coursesubmoduletracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="coursesubmoduletracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lpassessmenttracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="lpassessmenttracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="useralptracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="useralptracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="usercoursetracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="usercoursetracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userfavourite",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userfavourite",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userlearningpathtracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userlearningpathtracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userplaygroundgrouptracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userplaygroundgrouptracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userplaygroundtracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userplaygroundtracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userrating",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userrating",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userskilltravellertracker",
            name="ccms_id",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userskilltravellertracker",
            name="is_ccms_obj",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="assignmenttracker",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.assignment",
            ),
        ),
        migrations.AlterField(
            model_name="courseassessmenttracker",
            name="assessment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.courseassessment",
            ),
        ),
        migrations.AlterField(
            model_name="coursemoduletracker",
            name="module",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="learning.coursemodule",
            ),
        ),
        migrations.AlterField(
            model_name="coursesubmoduletracker",
            name="sub_module",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.coursesubmodule",
            ),
        ),
        migrations.AlterField(
            model_name="lpassessmenttracker",
            name="assessment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.lpassessment",
            ),
        ),
        migrations.AlterField(
            model_name="useralptracker",
            name="advanced_learning_path",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.advancedlearningpath",
            ),
        ),
        migrations.AlterField(
            model_name="usercoursetracker",
            name="course",
            field=models.ForeignKey(
                blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to="learning.course"
            ),
        ),
        migrations.AlterField(
            model_name="userlearningpathtracker",
            name="learning_path",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.learningpath",
            ),
        ),
        migrations.AlterField(
            model_name="userplaygroundgrouptracker",
            name="playground_group",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.playgroundgroup",
            ),
        ),
        migrations.AlterField(
            model_name="userplaygroundtracker",
            name="playground",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.playground",
            ),
        ),
        migrations.AlterField(
            model_name="userskilltravellertracker",
            name="skill_traveller",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="learning.skilltraveller",
            ),
        ),
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True)),
                ("ss_id", models.IntegerField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("user_level", "User Level"),
                            ("user_group_level", "User Group Level"),
                            ("tenant_level", "Tenant Level"),
                        ],
                        max_length=512,
                    ),
                ),
                ("text", models.TextField(blank=True, default=None, null=True)),
                ("user", models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ("user_group", models.ManyToManyField(blank=True, to="access_control.usergroup")),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_announcements",
            },
        ),
    ]