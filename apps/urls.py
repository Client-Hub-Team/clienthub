# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^', AppsAPI.as_view()),
]