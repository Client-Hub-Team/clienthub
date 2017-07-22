"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

# add the hellodjango project path into the sys.path
sys.path.append('/opt/clientadv-api/')

# add the virtualenv site-packages path to the sys.path
sys.path.append('/opt/clientadv-api/.venv/lib/python2.7/site-packages/')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
