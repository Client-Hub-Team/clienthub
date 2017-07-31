# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-07-31 00:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientManagement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='data',
            name='access_level',
            field=models.IntegerField(choices=[(2, 'Regular'), (1, 'Admin')], default=2),
        ),
        migrations.AddField(
            model_name='clientmanagement',
            name='accountant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accountant', to='user.Data'),
        ),
        migrations.AddField(
            model_name='clientmanagement',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to='user.Data'),
        ),
        migrations.AddField(
            model_name='data',
            name='clients',
            field=models.ManyToManyField(through='user.ClientManagement', to='user.Data'),
        ),
    ]