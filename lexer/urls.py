from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'lexer'
urlpatterns = [
    url(r'^$', views.complie, name='index'),
]
