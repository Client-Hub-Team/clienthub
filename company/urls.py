# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from company.views import *

urlpatterns = [
    url(r'^(?P<company_id>[^/]+)$', CompanyInfoAPI.as_view()),
    url(r'^(?P<company_id>[^/]+)/clients$', CompanyClientsAPI.as_view()),
    url(r'^(?P<company_id>[^/]+)/apps$', CompanyAppsAPI.as_view()),
    url(r'^(?P<company_id>[^/]+)/resources$', CompanyResourcesAPI.as_view()),
    url(r'^', CompanyAPI.as_view()),
]