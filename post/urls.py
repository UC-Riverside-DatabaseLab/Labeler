from django.conf.urls import url

from .views import *

app_name = 'post'

urlpatterns = [
  url(r'^create_post_response/(?P<task_pk>[-\w]+)&(?P<post_pk>[-\w]+)$', create_post_response, name='create_post_response'),
]