# Generated by Django 4.2.7 on 2025-03-19 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0014_formmaster'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldmaster',
            name='sub_control_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fieldmaster',
            name='sub_value',
            field=models.TextField(blank=True, null=True),
        ),
    ]
