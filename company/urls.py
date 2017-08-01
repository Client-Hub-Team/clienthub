# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from company.views import *

urlpatterns = [
    url(r'^create$', CompanyAPI.as_view()),
    url(r'^clients$', CompanyClientsAPI.as_view()),
]