# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-24 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiget', '0008_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='holeinfo',
            name='quarter',
            field=models.CharField(default='2017Q1', max_length=10),
            preserve_default=False,
        ),
    ]