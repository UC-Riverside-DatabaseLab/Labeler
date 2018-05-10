from django.conf.urls import url

from .views import *

app_name = 'response'

urlpatterns = [
  url(r'^create_post_response/(?P<task_pk>[-\w]+)&(?P<post_pk>[-\w]+)$', create_post_response, name='create_post_response'),
  url(r'^create_quiz_response(?P<pk>[-\w]+)$', create_quiz_response, name='create_quiz_response'),
]