# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-01 19:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_staffwithskills_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffwithskills',
            name='year',
            field=models.IntegerField(default=2017),
            preserve_default=False,
        ),
    ]