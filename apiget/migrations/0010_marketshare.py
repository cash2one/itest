# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-06 06:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiget', '0009_holeinfo_quarter'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketShare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productname', models.CharField(max_length=30)),
                ('date', models.CharField(max_length=10)),
                ('source', models.TextField()),
                ('sourcename', models.CharField(max_length=30)),
                ('platform', models.CharField(max_length=10)),
                ('type', models.CharField(max_length=10)),
            ],
        ),
    ]
