# Generated by Django 4.2.7 on 2025-05-12 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Workflow', '0018_referenceformstatus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referenceformstatus',
            old_name='form_data',
            new_name='form_data_id',
        ),
    ]
