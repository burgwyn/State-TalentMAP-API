# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-08 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bidding', '0009_bidcycle_cycle_deadline_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='status',
            field=models.TextField(choices=[('draft', 'draft'), ('submitted', 'submitted'), ('handshake offered', 'handshake offered'), ('handshake accepted', 'handshake accepted'), ('declined', 'declined'), ('closed', 'closed')], default='draft'),
        ),
    ]