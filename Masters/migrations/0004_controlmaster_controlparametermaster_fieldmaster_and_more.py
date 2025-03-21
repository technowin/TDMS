# Generated by Django 4.2.7 on 2025-03-12 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0003_send_user_department_send_user_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlMaster',
            fields=[
                ('control_id', models.AutoField(primary_key=True, serialize=False)),
                ('control_type_id', models.TextField(blank=True, null=True)),
                ('control_type', models.TextField(blank=True, null=True)),
                ('control_value', models.TextField(blank=True, null=True)),
                ('data_type', models.TextField(blank=True, null=True)),
                ('list_of_values', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'control_master',
            },
        ),
        migrations.CreateModel(
            name='ControlParameterMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_name', models.TextField(blank=True, null=True)),
                ('paramter_value', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'control_parameter_master',
            },
        ),
        migrations.CreateModel(
            name='FieldMaster',
            fields=[
                ('field_id', models.AutoField(primary_key=True, serialize=False)),
                ('control_id', models.TextField(blank=True, null=True)),
                ('control_type_id', models.TextField(blank=True, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'field_master',
            },
        ),
        migrations.CreateModel(
            name='FormMaster',
            fields=[
                ('form_id', models.AutoField(primary_key=True, serialize=False)),
                ('form_name', models.TextField(blank=True, null=True)),
                ('paramter_name', models.TextField(blank=True, null=True)),
                ('label_name', models.TextField(blank=True, null=True)),
                ('control_id', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'form_master',
            },
        ),
    ]
