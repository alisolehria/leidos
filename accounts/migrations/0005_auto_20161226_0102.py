# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-25 21:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_previousworkplaces'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='workStatus',
            field=models.CharField(choices=[(b'Working', b'Working'), (b'On Leave ', b'On Leave'), (b'Not Employeed', b'Not Employeed'), (b'Contractor', b'Contractor')], max_length=15),
        ),
    ]
