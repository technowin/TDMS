# Generated by Django 4.2.7 on 2025-04-01 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0062_rename_datatype_commonmaster_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formactionfield',
            old_name='action_id',
            new_name='action',
        ),
        migrations.AddField(
            model_name='formactionfield',
            name='dropdown_values',
            field=models.TextField(blank=True, null=True),
        ),
    ]
