# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-19 06:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiget', '0015_auto_20161219_1344'),
    ]

    operations = [
        migrations.RenameField(
            model_name='marketshare',
            old_name='type',
            new_name='myType',
        ),
        migrations.RenameField(
            model_name='productsshare',
            old_name='type',
            new_name='myType',
        ),
    ]
