# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-15 05:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiget', '0005_holeinfo_groupname'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestInfos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quarter', models.CharField(max_length=8)),
                ('group', models.CharField(max_length=20)),
                ('bugs_found', models.IntegerField()),
                ('bugs_found_p1', models.IntegerField()),
                ('bugs_escape', models.IntegerField()),
                ('bugs_escape_noduty', models.IntegerField()),
                ('bugs_escape_p1', models.IntegerField()),
                ('bugs_escape_p1_noduty', models.IntegerField()),
                ('bugs_escape_info', models.TextField()),
                ('bugs_found_function', models.IntegerField()),
                ('bugs_found_function_p1', models.IntegerField()),
                ('bugs_other', models.IntegerField()),
                ('bugs_other_p1', models.IntegerField()),
                ('allow_tests', models.IntegerField()),
                ('allow_tests_pass', models.IntegerField()),
                ('t_id', models.CharField(max_length=8)),
            ],
        ),
    ]