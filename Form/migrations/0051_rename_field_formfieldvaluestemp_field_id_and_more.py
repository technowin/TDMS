# Generated by Django 4.2.7 on 2025-05-13 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Form', '0050_workflowversioncontrol_file_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formfieldvaluestemp',
            old_name='field',
            new_name='field_id',
        ),
        migrations.RenameField(
            model_name='formfieldvaluestemp',
            old_name='form_data',
            new_name='form_data_id',
        ),
    ]
