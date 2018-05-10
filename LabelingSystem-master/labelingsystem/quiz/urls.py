from django.conf.urls import url

from .views import *

app_name = 'quiz'

urlpatterns = [
  url(r'^take_quiz/(?P<pk>[-\w]+)$', TakeQuizView.as_view(), name='take_quiz'),
  url(r'^quiz_success/(?P<pk>[-\w]+)$', QuizSuccessView.as_view(), name='quiz_success'),
  url(r'^create_quiz/$', CreateQuizView.as_view(), name='create_quiz'),
  url(r'^create_quiz_success/$', CreateQuizSuccessView.as_view(), name='create_quiz_success'),
  url(r'^quiz_fail/(?P<pk>[-\w]+)$', QuizFailView.as_view(), name='quiz_fail'),
]
