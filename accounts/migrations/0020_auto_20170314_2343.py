# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-14 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_auto_20170314_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=b'../adminUser/static/img/'),
        ),
    ]
