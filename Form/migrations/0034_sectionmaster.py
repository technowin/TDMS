# Generated by Django 4.2.7 on 2025-05-06 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Form', '0033_formfield_section'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'section_master',
            },
        ),
    ]
