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
    access_level = models.IntegerField(choices=USERLEVEL_CHOICES, default=REGULAR, null=True)
    created = models.DateTimeField(auto_now=True)


class Invite(models.Model):

    COMPANY_CREATE = 1
    COMPANY_JOIN = 2

    TYPE_CHOICES = (
        (COMPANY_CREATE, 'Create Company'),
        (COMPANY_JOIN, 'Join Company')
    )

    accountant = models.ForeignKey(User, db_index=True, related_name="invite_accountant", null=True)
    client = models.ForeignKey(User, db_index=True, related_name="invite_client", null=True)
    name = models.CharField(max_length=250, null=False, blank=False)
    email = models.CharField(max_length=250, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    type = models.IntegerField(choices=TYPE_CHOICES, default=COMPANY_JOIN, null=False)



