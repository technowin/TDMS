# Generated by Django 4.2.7 on 2025-05-29 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0003_customuser_file_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='error_log',
            name='user',
            field=models.TextField(blank=True, null=True),
        ),
    ]
