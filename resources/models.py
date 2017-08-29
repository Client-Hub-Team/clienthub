# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from company.models import Company
from django.contrib.auth.models import User

class Resource(models.Model):

    name = models.CharField(max_length=250, null=False, blank=False)
    file_type = models.TextField(max_length=250, null=True, blank=True)
    description = models.TextField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    company = models.ForeignKey(Company, null=True, blank=True, default=None)


class CompanyHasResource(models.Model):

    class Meta:
        ordering = ['order']

    resource = models.ForeignKey(Resource)
    company = models.ForeignKey(Company)
    created = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True)


class UserHasResource(models.Model):

    resource = models.ForeignKey(Resource)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now=True)
    order = models.IntegerField(blank=True, null=True)
