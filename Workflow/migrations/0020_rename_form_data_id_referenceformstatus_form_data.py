# Generated by Django 4.2.7 on 2025-05-12 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Workflow', '0019_rename_form_data_referenceformstatus_form_data_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referenceformstatus',
            old_name='form_data_id',
            new_name='form_data',
        ),
    ]
