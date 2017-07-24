# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Practice(models.Model):

    name = models.CharField(max_length=250, null=False, blank=False)
    logo = models.TextField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    twitter = models.CharField(max_length=250, null=True, blank=True)