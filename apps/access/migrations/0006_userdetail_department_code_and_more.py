# Generated by Django 4.2.3 on 2023-12-28 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meta", "0011_departmentcode_departmenttitle_employmentstatus_and_more"),
        ("access", "0005_alter_user_uuid_alter_userconnection_uuid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdetail",
            name="department_code",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="meta.departmentcode",
            ),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="department_title",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="meta.departmenttitle",
            ),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="employee_id",
            field=models.CharField(blank=True, default=None, max_length=512, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="employment_start_date",
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="employment_status",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="meta.employmentstatus",
            ),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="job_description",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="meta.jobdescription",
            ),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="job_title",
            field=models.ForeignKey(
                blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to="meta.jobtitle"
            ),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="manager_three_email",
            field=models.EmailField(blank=True, default=None, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="userdetail",
            name="manager_two_email",
            field=models.EmailField(blank=True, default=None, max_length=254, null=True),
        ),
    ]