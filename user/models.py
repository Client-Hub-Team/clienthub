# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from practice.models import Practice
from django.contrib.auth.models import User

class Data(models.Model):
    ACCOUNTANT = 1
    CLIENT = 2

    USERTYPE_CHOICES = (
        (ACCOUNTANT, 'Accountant'),
        (CLIENT, 'Client'),
    )

    ADMIN = 1
    REGULAR = 2


    USERLEVEL_CHOICES = (
        (REGULAR, 'Regular'),
        (ADMIN, 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    practice = models.ForeignKey(Practice, null=True, blank=True)
    user_type = models.IntegerField(choices=USERTYPE_CHOICES, default=ACCOUNTANT, null=False)
    access_level = models.IntegerField(choices=USERLEVEL_CHOICES, default=REGULAR, null=False)
    created = models.DateTimeField(auto_now=True)
    clients = models.ManyToManyField('Data', through='ClientManagement')


class Invite(models.Model):

    invited_by = models.ForeignKey(User, db_index=True, related_name="invited_by", null=True)
    name = models.CharField(max_length=250, null=False, blank=False)
    email = models.CharField(max_length=250, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    type = models.IntegerField(choices=Data.USERTYPE_CHOICES, default=Data.ACCOUNTANT, null=False)


class ClientManagement(models.Model):
    accountant = models.ForeignKey(Data, related_name='accountant')
    client = models.ForeignKey(Data, related_name='client')



