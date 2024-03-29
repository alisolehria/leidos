# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-15 20:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adminUser', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='alerts',
            fields=[
                ('alertID', models.AutoField(primary_key=True, serialize=False)),
                ('alertType', models.CharField(choices=[(b'Project', b'Project'), (b'Leave', b'Leave'), (b'Staff', b'Staff'), (b'Edit Project', b'Edit Project'), (b'Edit Staff', b'Edit Staff'), (b'Project Request', b'Project Request')], max_length=30)),
                ('alertDate', models.DateField()),
                ('info', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'db_table': 'alerts',
            },
        ),
        migrations.CreateModel(
            name='holidays',
            fields=[
                ('holidayID', models.AutoField(primary_key=True, serialize=False)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('type', models.CharField(choices=[(b'Sick', b'Sick'), (b'Emergency', b'Emergency'), (b'Vacation', b'Vacation')], max_length=30)),
                ('status', models.CharField(choices=[(b'Approved', b'Approved'), (b'Pending Approval', b'Pending Approval'), (b'Declined', b'Declined')], max_length=30)),
            ],
            options={
                'db_table': 'holidays',
            },
        ),
        migrations.CreateModel(
            name='previousWorkplaces',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('companyName', models.CharField(max_length=200)),
                ('companyRating', models.IntegerField()),
            ],
            options={
                'db_table': 'previousWorkplaces',
            },
        ),
        migrations.CreateModel(
            name='profile',
            fields=[
                ('staffID', models.AutoField(primary_key=True, serialize=False)),
                ('dateOfBirth', models.DateField()),
                ('nationality', models.CharField(max_length=200)),
                ('contact', models.CharField(max_length=12)),
                ('gender', models.CharField(choices=[(b'Male', b'Male'), (b'Female', b'Female')], max_length=6)),
                ('designation', models.CharField(choices=[(b'Admin', b'Admin'), (b'Project Manager', b'Project Manager'), (b'Employee', b'Employee')], max_length=15)),
                ('workStatus', models.CharField(choices=[(b'Working', b'Working'), (b'On Leave ', b'On Leave'), (b'Not Employeed', b'Not Employeed'), (b'Contractor', b'Contractor')], max_length=15)),
                ('skillLevel', models.IntegerField()),
                ('salary', models.IntegerField()),
                ('preferredLocation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminUser.location')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profile',
            },
        ),
        migrations.CreateModel(
            name='projects',
            fields=[
                ('projectID', models.AutoField(primary_key=True, serialize=False)),
                ('projectName', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[(b'Consultancy', b'Consultancy'), (b'Development', b'Development'), (b'Delivery', b'Delivery'), (b'IT', b'IT')], max_length=30)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('description', models.TextField()),
                ('budget', models.IntegerField()),
                ('numberOfStaff', models.IntegerField()),
                ('status', models.CharField(choices=[(b'Pending Approval', b'Pending Approval'), (b'Approved', b'Approved'), (b'On Going', b'On Going'), (b'Completed', b'Completed'), (b'Declined', b'Declined'), (b'Discontinued', b'Discontinued')], max_length=30)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminUser.location')),
                ('projectManager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.profile')),
            ],
            options={
                'db_table': 'projects',
            },
        ),
        migrations.CreateModel(
            name='projectsWithSkills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hoursRequired', models.IntegerField()),
                ('projectID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.projects')),
            ],
            options={
                'db_table': 'projectsWithSkills',
            },
        ),
        migrations.CreateModel(
            name='skills',
            fields=[
                ('skillID', models.AutoField(primary_key=True, serialize=False)),
                ('skillName', models.CharField(max_length=200)),
                ('projectID', models.ManyToManyField(through='accounts.projectsWithSkills', to='accounts.projects')),
            ],
            options={
                'db_table': 'skills',
            },
        ),
        migrations.CreateModel(
            name='staffAlerts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seenDate', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[(b'Seen', b'Seen'), (b'Unseen', b'Unseen')], default=b'Unseen', max_length=30)),
                ('alertID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.alerts')),
                ('staffID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
            ],
            options={
                'db_table': 'staffAlerts',
            },
        ),
        migrations.CreateModel(
            name='staffWithProjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(b'Working', b'Working'), (b'Not Working', b'Not Working')], max_length=30)),
                ('profile_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
                ('projects_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.projects')),
            ],
            options={
                'db_table': 'staffWithProjects',
            },
        ),
        migrations.CreateModel(
            name='staffWithSkills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hoursAvailable', models.IntegerField()),
                ('skillID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.skills')),
                ('staffID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
            ],
            options={
                'db_table': 'staffWithSkills',
            },
        ),
        migrations.AddField(
            model_name='skills',
            name='staffID',
            field=models.ManyToManyField(through='accounts.staffWithSkills', to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='projectswithskills',
            name='skillID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.skills'),
        ),
        migrations.AddField(
            model_name='projects',
            name='staffID',
            field=models.ManyToManyField(through='accounts.staffWithProjects', to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='previousworkplaces',
            name='staffID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='holidays',
            name='staffID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='alerts',
            name='fromStaff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='alerts',
            name='holiday',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.holidays'),
        ),
        migrations.AddField(
            model_name='alerts',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.projects'),
        ),
        migrations.AddField(
            model_name='alerts',
            name='staff',
            field=models.ManyToManyField(blank=True, through='accounts.staffAlerts', to='accounts.profile'),
        ),
    ]
