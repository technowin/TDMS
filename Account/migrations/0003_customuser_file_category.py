# Generated by Django 4.2.7 on 2025-05-27 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0002_common_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='file_category',
            field=models.TextField(blank=True, null=True),
        ),
    ]
