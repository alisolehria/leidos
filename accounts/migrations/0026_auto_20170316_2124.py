# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-16 17:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_auto_20170316_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='boardComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('time', models.DateField()),
            ],
            options={
                'db_table': 'boardComments',
            },
        ),
        migrations.CreateModel(
            name='messageBoard',
            fields=[
                ('boardID', models.AutoField(primary_key=True, serialize=False)),
                ('comments', models.ManyToManyField(through='accounts.boardComments', to='accounts.profile')),
                ('projectID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.projects')),
            ],
            options={
                'db_table': 'messageBoard',
            },
        ),
        migrations.AddField(
            model_name='boardcomments',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.messageBoard'),
        ),
        migrations.AddField(
            model_name='boardcomments',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile'),
        ),
    ]
