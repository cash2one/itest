# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-20 02:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiget', '0017_productsshare_datetype'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productsshare',
            old_name='pvalue',
            new_name='pv',
        ),
        migrations.RenameField(
            model_name='productsshare',
            old_name='uvalue',
            new_name='uv',
        ),
    ]