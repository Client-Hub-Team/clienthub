# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-08-17 22:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientManagement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.IntegerField(choices=[(1, 'Accountant'), (2, 'Client')], default=1)),
                ('access_level', models.IntegerField(choices=[(2, 'Regular'), (1, 'Admin')], default=2)),
                ('created', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('email', models.CharField(blank=True, max_length=250, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('type', models.IntegerField(choices=[(1, 'Accountant'), (2, 'Client')], default=1)),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invited_by', to=settings.AUTH_USER_MODEL)),
                ('invited_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
            ],
        ),
        migrations.AddField(
            model_name='clientmanagement',
            name='accountant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accountant', to='user.Data'),
        ),
        migrations.AddField(
            model_name='clientmanagement',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_company', to='company.Company'),
        ),
    ]
