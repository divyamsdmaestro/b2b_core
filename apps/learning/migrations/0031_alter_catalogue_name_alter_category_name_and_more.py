# Generated by Django 4.2.3 on 2024-01-05 11:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0030_remove_catalogue_user_group_catalogue_ccms_alp_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="catalogue",
            name="name",
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name="categoryrole",
            name="name",
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name="categoryskill",
            name="name",
            field=models.CharField(max_length=512),
        ),
    ]
