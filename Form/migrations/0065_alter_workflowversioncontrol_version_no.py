# Generated by Django 4.2.7 on 2025-05-22 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Form', '0064_actiondata_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowversioncontrol',
            name='version_no',
            field=models.TextField(blank=True, null=True),
        ),
    ]
