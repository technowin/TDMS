# Generated by Django 4.2.7 on 2025-03-25 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0037_rename_contromasters_controlmasters_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formmaster',
            name='form_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
