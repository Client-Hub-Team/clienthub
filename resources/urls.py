# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^', ResourcesAPI.as_view()),
]