# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_practice = models.BooleanField(blank=False, null=False, default=True)
    date_registered = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(User, related_name='manager', null=True)
