# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-07 15:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0006_auto_20171205_1627'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='string_representation',
            new_name='_string_representation',
        ),
        migrations.RenameField(
            model_name='sharable',
            old_name='string_representation',
            new_name='_string_representation',
        ),
    ]
