# Generated by Django 4.2.7 on 2025-03-26 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0049_remove_formfield_sub_control_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='created_by',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='form',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='form',
            name='updated_by',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='form',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
