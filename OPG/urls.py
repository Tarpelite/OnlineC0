from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'OPG'
urlpatterns = [
    url(r'^$', views.complie, name='index'),
]
