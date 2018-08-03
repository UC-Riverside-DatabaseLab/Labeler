from django.conf.urls import url

from .views import *
app_name = 'task'

urlpatterns = [
  url(r'^task_list/$', TaskListView.as_view(), name='task_list'),
  url(r'^create_task/get_table/$', get_table, name = "get_table_all"),
  url(r'^create_task/get_table_all/$', get_table_all, name = "get_table"),
  url(r'^take_task/(?P<pk>[-\w]+)$', TakeTaskView.as_view(), name='take_task'),
  url(r'^task_complete/$', TaskCompleteView.as_view(), name='task_complete'),
  url(r'^task_empty/$', TaskEmptyView.as_view(), name='task_empty'),
  url(r'^create_task/$', CreateTaskView.as_view(), name='create_task'),
  url(r'^create_task_success/$', CreateTaskSuccessView.as_view(), name='create_task_success'),
  url(r'^load_database/$', LoadDatabaseView.as_view(), name='load_database'),
  url(r'^load_database_success/$', LoadDatabaseSuccessView.as_view(), name='load_database_success'),
  url(r'^load_database_fail/$', LoadDatabaseFailView.as_view(), name='load_database_fail'),
  url(r'^edit_task/$', EditTaskView.as_view(), name='edit_task'),
  url(r'^edit_task_success/$', EditTaskSuccessView.as_view(), name='edit_task_success'),
  url(r'^update_labeler/$', UpdateLabelerView.as_view(), name='update_labeler'),
  url(r'^update_labeler_success/$', UpdateLabelerSuccessView.as_view(), name='update_labeler_success'),
  url(r'^task_evaluation_list/$', TaskEvaluationListView.as_view(), name='task_evaluation_list'),
  url(r'^task_evaluation_empty/$', TaskEvaluationEmptyView.as_view(), name='task_evaluation_empty'),
  url(r'^task_evaluation_detail/(?P<pk>[-\w]+)$', TaskEvaluationDetailView.as_view(), name='task_evaluation_detail'),
  url(r'^task_participation_list/$', TaskParticipationListView.as_view(), name='task_participation_list'),
  url(r'^task_participation_empty/$', TaskParticipationEmptyView.as_view(), name='task_participation_empty'),
  url(r'^connection_list/$', ConnectionListView.as_view(), name='connection_list'),
  url(r'^connection_list/delete_connection/$', delete_connection, name='delete_connection'),
  url(r'^connection_list/(?P<pk>\d+)/$', ConnectionDetailView.as_view(), name='connection_detail'),
  url(r'^connection_list_modal/$', ConnectionListModalView.as_view(), name='connection_list_modal'),
  url(r'^connection_list_modal/delete_connection_modal/$', delete_connection_modal, name='delete_connection_modal'),
  url(r'^connection_list_modal/(?P<pk>\d+)/$', ConnectionDetailModalView.as_view(), name='connection_detail_modal'),
  url(r'^load_database_modal/$', LoadDatabaseModalView.as_view(), name='load_database_modal'),
  url(r'^load_database_success_modal/$', LoadDatabaseSuccessModalView.as_view(), name='load_database_success_modal'),
  url(r'^load_database_fail_modal/$', LoadDatabaseFailModalView.as_view(), name='load_database_fail_modal'),
]


