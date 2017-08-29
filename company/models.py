# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):

    name = models.CharField(max_length=250, null=False, blank=False)
    logo = models.TextField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    twitter = models.CharField(max_length=250, null=True, blank=True)
    facebook = models.CharField(max_length=250, null=True, blank=True)
    linkedin = models.CharField(max_length=250, null=True, blank=True)
    is_accounting = models.BooleanField(default=False)
    owner = models.ForeignKey(User, null=True, blank=True, default=None)
    accounting_company = models.ForeignKey("Company", null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True, default="#FFF")