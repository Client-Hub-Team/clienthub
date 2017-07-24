# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from practice.views import *

urlpatterns = [
    url(r'^create$', PracticeAPI.as_view()),
]