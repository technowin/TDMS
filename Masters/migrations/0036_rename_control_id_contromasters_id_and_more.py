# Generated by Django 4.2.7 on 2025-03-25 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0035_contromasters_alter_formfield_field_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contromasters',
            old_name='control_id',
            new_name='id',
        ),
        migrations.RemoveField(
            model_name='contromasters',
            name='control_type_id',
        ),
    ]
