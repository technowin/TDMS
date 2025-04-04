# Generated by Django 4.2.7 on 2025-03-25 07:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0033_controlparametermaster_control_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'form',
            },
        ),
        migrations.RemoveField(
            model_name='formfield',
            name='options',
        ),
        migrations.AddField(
            model_name='formfield',
            name='disable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='formfield',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='formfield',
            name='required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='formfield',
            name='row_position',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='formfield',
            name='searchable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='field_type',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterModelTable(
            name='formfield',
            table='form_field',
        ),
        migrations.CreateModel(
            name='FieldValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.CharField(choices=[('min_length', 'Min Length'), ('max_length', 'Max Length'), ('regex', 'Regex'), ('custom', 'Custom Rule')], max_length=50)),
                ('value', models.CharField(max_length=255)),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='validations', to='Masters.formfield')),
            ],
        ),
        migrations.CreateModel(
            name='FieldDependency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(max_length=255)),
                ('dependent_on', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dependent_fields', to='Masters.formfield')),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dependencies', to='Masters.formfield')),
            ],
            options={
                'db_table': 'field_dependeny',
            },
        ),
        migrations.AddField(
            model_name='formfield',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='Masters.form'),
        ),
    ]
