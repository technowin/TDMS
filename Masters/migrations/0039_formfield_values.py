# Generated by Django 4.2.7 on 2025-03-25 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0038_formmaster_form_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfield',
            name='values',
            field=models.TextField(blank=True, null=True),
        ),
    ]
