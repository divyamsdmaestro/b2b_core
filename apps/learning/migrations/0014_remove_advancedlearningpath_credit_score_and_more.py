# Generated by Django 4.2.3 on 2023-11-28 08:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0013_remove_course_forums_alter_coursemodule_end_date_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="advancedlearningpath",
            name="credit_score",
        ),
        migrations.RemoveField(
            model_name="advancedlearningpath",
            name="is_mandatory_dependencies_complete",
        ),
        migrations.RemoveField(
            model_name="advancedlearningpath",
            name="requirements",
        ),
        migrations.RemoveField(
            model_name="assignment",
            name="requirements",
        ),
        migrations.RemoveField(
            model_name="course",
            name="credit_score",
        ),
        migrations.RemoveField(
            model_name="course",
            name="is_mandatory_dependencies_complete",
        ),
        migrations.RemoveField(
            model_name="course",
            name="requirements",
        ),
        migrations.RemoveField(
            model_name="coursemodule",
            name="is_ans_visible_pe",
        ),
        migrations.RemoveField(
            model_name="coursemodule",
            name="is_assignment_dependent",
        ),
        migrations.RemoveField(
            model_name="coursemodule",
            name="is_module_assessment_dependent",
        ),
        migrations.RemoveField(
            model_name="coursemodule",
            name="is_sub_module_sequence",
        ),
        migrations.RemoveField(
            model_name="learningpath",
            name="credit_score",
        ),
        migrations.RemoveField(
            model_name="learningpath",
            name="is_mandatory_dependencies_complete",
        ),
        migrations.RemoveField(
            model_name="learningpath",
            name="requirements",
        ),
        migrations.RemoveField(
            model_name="playground",
            name="credit_score",
        ),
        migrations.RemoveField(
            model_name="playground",
            name="is_mandatory_dependencies_complete",
        ),
        migrations.RemoveField(
            model_name="playground",
            name="requirements",
        ),
        migrations.RemoveField(
            model_name="playgroundgroup",
            name="credit_score",
        ),
        migrations.RemoveField(
            model_name="playgroundgroup",
            name="is_mandatory_dependencies_complete",
        ),
        migrations.RemoveField(
            model_name="playgroundgroup",
            name="requirements",
        ),
        migrations.RemoveField(
            model_name="skilltraveller",
            name="credit_score",
        ),
        migrations.RemoveField(
            model_name="skilltraveller",
            name="is_mandatory_dependencies_complete",
        ),
        migrations.RemoveField(
            model_name="skilltraveller",
            name="requirements",
        ),
        migrations.AlterField(
            model_name="catalogue",
            name="name",
            field=models.CharField(max_length=512, unique=True),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=512, unique=True),
        ),
        migrations.AlterField(
            model_name="categoryrole",
            name="name",
            field=models.CharField(max_length=512, unique=True),
        ),
        migrations.AlterField(
            model_name="categoryskill",
            name="name",
            field=models.CharField(max_length=512, unique=True),
        ),
    ]
