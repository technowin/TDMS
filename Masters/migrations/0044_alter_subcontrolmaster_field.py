# Generated by Django 4.2.7 on 2025-03-26 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0043_alter_fielddependency_table_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcontrolmaster',
            name='field',
            field=models.TextField(blank=True, null=True),
        ),
    ]
