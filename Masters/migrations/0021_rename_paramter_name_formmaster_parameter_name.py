# Generated by Django 4.2.7 on 2025-03-19 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0020_remove_fieldmaster_control_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formmaster',
            old_name='paramter_name',
            new_name='parameter_name',
        ),
    ]
