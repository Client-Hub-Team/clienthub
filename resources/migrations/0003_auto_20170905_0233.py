# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-09-05 05:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_auto_20170831_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='file_type',
            field=models.IntegerField(choices=[(1, 'Document'), (2, 'Spreadsheet'), (3, 'Video'), (4, 'Image'), (5, 'Other')], default=1, null=True),
        ),
    ]
