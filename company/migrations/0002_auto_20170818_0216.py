# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-08-18 05:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='facebook',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='linkedin',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
