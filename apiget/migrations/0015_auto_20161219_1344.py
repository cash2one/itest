# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-19 05:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiget', '0014_marketshare_remarks'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductsShare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productname', models.CharField(max_length=30)),
                ('pvalue', models.IntegerField()),
                ('uvalue', models.IntegerField()),
                ('date', models.CharField(max_length=10)),
                ('itemname', models.CharField(max_length=30)),
                ('platform', models.CharField(max_length=10)),
                ('type', models.CharField(max_length=10)),
                ('remarks', models.TextField()),
            ],
        ),
        migrations.RenameField(
            model_name='marketshare',
            old_name='productname',
            new_name='itemname',
        ),
    ]