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



