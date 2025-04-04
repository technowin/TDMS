# Generated by Django 4.2.7 on 2025-03-25 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0034_form_remove_formfield_options_formfield_disable_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControMasters',
            fields=[
                ('control_id', models.AutoField(primary_key=True, serialize=False)),
                ('control_type_id', models.IntegerField(blank=True, null=True)),
                ('control_type', models.TextField(blank=True, null=True)),
                ('control_value', models.TextField(blank=True, null=True)),
                ('data_type', models.TextField(blank=True, null=True)),
                ('sub_master1', models.IntegerField(blank=True, null=True)),
                ('sub_master2', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'control_masters',
            },
        ),
        migrations.AlterField(
            model_name='formfield',
            name='field_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
