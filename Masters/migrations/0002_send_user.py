# Generated by Django 4.2.7 on 2025-01-23 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='send_user',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'send_user',
            },
        ),
    ]
