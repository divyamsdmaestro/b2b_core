# Generated by Django 4.2.3 on 2024-01-08 07:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0032_alter_advancedlearningpathimagemodel_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="advancedlearningpath",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="assignment",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="learningpath",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="playground",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="playgroundgroup",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="roleskillrelation",
            name="required_proficiency",
            field=models.CharField(
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                max_length=512,
            ),
        ),
        migrations.AlterField(
            model_name="skilltraveller",
            name="proficiency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advance", "Advance"),
                    ("comprehensive", "Comprehensive"),
                    ("certification", "Certification"),
                    ("conversant", "Conversant"),
                    ("general", "General"),
                ],
                default=None,
                max_length=512,
                null=True,
            ),
        ),
    ]