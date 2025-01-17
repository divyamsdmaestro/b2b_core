# Generated by Django 4.2.3 on 2024-01-06 11:37

import apps.common.helpers
import apps.common.model_fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0004_alter_forum_uuid_alter_forumcourserelationmodel_uuid_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forumimagemodel",
            name="image",
            field=apps.common.model_fields.AppImageField(
                max_length=512, max_size=5, upload_to=apps.common.helpers.file_upload_path
            ),
        ),
        migrations.AlterField(
            model_name="postimagemodel",
            name="image",
            field=apps.common.model_fields.AppImageField(
                max_length=512, max_size=5, upload_to=apps.common.helpers.file_upload_path
            ),
        ),
    ]
