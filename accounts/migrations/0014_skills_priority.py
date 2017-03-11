# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-10 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_staffprojectskill_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills',
            name='priority',
            field=models.CharField(blank=True, choices=[(b'High', b'High'), (b'Mid', b'Mid'), (b'Low', b'Low')], max_length=30, null=True),
        ),
    ]