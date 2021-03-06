# Generated by Django 2.2 on 2019-04-16 13:26

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsnap_registration', '0002_auto_20190308_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='original_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(editable=False),
        ),
    ]
