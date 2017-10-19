# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-12 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0013_remove_country_is_territory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='short_code',
            field=models.TextField(db_index=True, help_text='The unique 2-character country code'),
        ),
    ]