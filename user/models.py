# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from company.models import Company
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


    ACCESSLEVEL_CHOICES = (
        (REGULAR, 'Regular'),
        (ADMIN, 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, null=True, blank=True)
    user_type = models.IntegerField(choices=USERTYPE_CHOICES, default=ACCOUNTANT, null=False)
    access_level = models.IntegerField(choices=ACCESSLEVEL_CHOICES, default=REGULAR, null=False)
    created = models.DateTimeField(auto_now=True)


class Invite(models.Model):

    invited_by = models.ForeignKey(User, db_index=True, related_name="invited_by", null=True)
    name = models.CharField(max_length=250, null=False, blank=False)
    email = models.CharField(max_length=250, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    invited_to = models.ForeignKey(Company, null=True)
    accepted = models.BooleanField(default=False)
    type = models.IntegerField(choices=Data.USERTYPE_CHOICES, default=Data.ACCOUNTANT, null=False)


class ClientManagement(models.Model):
    accountant = models.ForeignKey(Data, related_name='accountant')
    company = models.ForeignKey(Company, related_name='managed_company')
    created = models.DateTimeField(auto_now=True)



