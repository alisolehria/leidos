# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-15 20:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffwithprojects',
            name='status',
            field=models.CharField(blank=True, choices=[(b'Working', b'Working'), (b'Not Working', b'Not Working')], max_length=30, null=True),
        ),
    ]
