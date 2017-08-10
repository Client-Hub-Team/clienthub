"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from user import urls as user_urls
from company import urls as company_urls
from apps import urls as app_urls
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^user/', include(user_urls)),
    url(r'^company/', include(company_urls)),
    url(r'^apps/', include(app_urls)),
]
