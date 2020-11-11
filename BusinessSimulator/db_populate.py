import os

#
#   Important!  You need to run this file when installing the database 
#               and after anysequent database flushes
#
#
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'BusinessSimulator.settings')

import django
from django.core.files import File

django.setup()


from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

