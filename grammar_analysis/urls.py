from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'grammar_analysis'
urlpatterns = [
    url(r'^$', views.compile, name='index'),
]
