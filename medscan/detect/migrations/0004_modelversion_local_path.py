# Generated by Django 4.2.5 on 2023-09-22 17:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("detect", "0003_alter_job_model_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelversion",
            name="local_path",
            field=models.CharField(
                blank=True, editable=False, max_length=255, null=True
            ),
        ),
    ]
