# Generated by Django 4.2.7 on 2025-03-21 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0024_remove_formfieldmaster_form_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfieldmaster',
            name='control_master_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
