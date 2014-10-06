# coding: utf8

from settings import *

DEBUG = False

ALLOWED_HOSTS = (os.environ['HOST_NAME'],)
SECRET_KEY = (os.environ['SECRET_KEY'],)
