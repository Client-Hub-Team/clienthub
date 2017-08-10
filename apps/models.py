# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class App(models.Model):

    name = models.CharField(max_length=250, null=False, blank=False)
    category = models.TextField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    logo = models.CharField(max_length=250, null=True, blank=True)


class UserHasApp(models.Model):

    app = models.ForeignKey(App)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True)
