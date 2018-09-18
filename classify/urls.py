from django.conf.urls import url

from .views import *

app_name = 'classify'

urlpatterns = [
  url(r'^create_classification_model/$', CreateClassificationModelView.as_view(), name='create_classification_model'),
  url(r'^create_classification_model_success/$', CreateClassificationModelSuccessView.as_view(), name='create_classification_model_success'),
  url(r'^classify_data/$', ClassifyDataView.as_view(), name='classify_data'),
  url(r'^classify_success/$', ClassifySuccessView.as_view(), name='classify_success'),
  url(r'^classify_list/$', ClassifyTaskListView.as_view(), name='classify_list'),
  url(r'^delete_classify/(?P<pk>\d+)/$', DeleteClassifyView.as_view(), name='delete_classify'),
]
