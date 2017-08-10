# -*- coding:utf-8 -*-

# urls.py
from django.conf.urls import url
from user.views import *

urlpatterns = [
    url(r'^create$', AccountAPI.as_view()),
    url(r'^invite$', InviteClient.as_view()),
    url(r'^invite.check$', CheckInvitation.as_view()),
    url(r'^accountant.client.add', AddClientToAccountant.as_view()),
    url(r'^accountant.client.list', AccountantClientsAPI.as_view()),
    url(r'^(?P<user_id>[^/]+)$', ClientInfoAPI.as_view()),
    url(r'^(?P<user_id>[^/]+)/apps$', ClientAppsAPI.as_view()),
]