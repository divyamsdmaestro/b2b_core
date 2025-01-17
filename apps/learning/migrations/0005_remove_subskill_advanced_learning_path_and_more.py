# Generated by Django 4.2.3 on 2023-11-08 20:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("my_learning", "0009_remove_subskilltrackingmodel_created_by_and_more"),
        ("learning", "0004_expert"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subskill",
            name="advanced_learning_path",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="category",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="course",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="deleted_by",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="forums",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="hashtag",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="image",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="language",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="learning_path",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="modified_by",
        ),
        migrations.RemoveField(
            model_name="subskill",
            name="skill",
        ),
        migrations.RemoveField(
            model_name="catalogue",
            name="no_of_sub_role",
        ),
        migrations.RemoveField(
            model_name="catalogue",
            name="no_of_sub_skill",
        ),
        migrations.RemoveField(
            model_name="catalogue",
            name="sub_role",
        ),
        migrations.RemoveField(
            model_name="catalogue",
            name="sub_skill",
        ),
        migrations.RemoveField(
            model_name="categoryrole",
            name="no_of_sub_role",
        ),
        migrations.RemoveField(
            model_name="categoryskill",
            name="no_of_sub_skill",
        ),
        migrations.DeleteModel(
            name="SubRole",
        ),
        migrations.DeleteModel(
            name="SubRoleImageModel",
        ),
        migrations.DeleteModel(
            name="SubSkill",
        ),
        migrations.DeleteModel(
            name="SubSkillImageModel",
        ),
    ]
