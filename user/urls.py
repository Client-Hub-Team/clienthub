# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from user.views import UserDataAPI, AccountAPI

urlpatterns = [
    url(r'^create$', AccountAPI.as_view()),
]