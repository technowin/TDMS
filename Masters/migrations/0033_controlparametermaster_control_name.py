# Generated by Django 4.2.7 on 2025-03-25 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0032_formfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlparametermaster',
            name='control_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
