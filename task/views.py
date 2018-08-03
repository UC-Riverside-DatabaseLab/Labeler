from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, FormView, DetailView, DeleteView
from .models import Task, Participation,Document, Connection,Colname, Tablename
from label.models import Label
from post.models import Post
from response.models import PostResponse
from collections import deque
from collections import Counter
from .forms import CreateTaskForm
from .forms import EditTaskForm
from .forms import LoadDatabaseForm
from flask import Flask, request
from .forms import UpdateLabelerForm
from nltk.metrics.agreement import AnnotationTask
from django.http import HttpResponseRedirect, HttpResponse
from itertools import combinations
import requests
import pymysql
import csv
import datetime
import os
from io import TextIOWrapper
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import random
from django.db.models import Q
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
User = get_user_model()

'''get database table data and return the result'''
@csrf_exempt
def get_table(request):
  print('123')
  if request.is_ajax() and request.method == 'POST':
    table_id = request.POST.get('table_id', '')
    print(table_id)
    table = Tablename.objects.get(id=int(table_id))
    db = Connection.objects.get(id=table.connection.id)
    print(db.id)
    if db.is_mysql:
      print("load from mysql")
      try:
        connection = pymysql.connect(host=db.ip,
                                     port=db.port,
                                     user=db.username,
                                     password=db.password,
                                     db=db.dbname,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor
                                     )
        with connection.cursor() as cursor:
          cursor.execute("SELECT * FROM " + table.tablename + " LIMIT 10")
          result = cursor.fetchall()
          data = json.dumps(result)
      except:
        return None
    else:
      print("load from asterix")
      url = 'http://' + db.ip + ':' + str(db.port) + '/query/service'
      print(url)
      statement = 'use ' + db.dbname + ';'
      data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
      res = requests.post(url, params=data_dict)
      print(res.status_code)
      if res.status_code != 200:
        return None
      statement = "SELECT * FROM " + table.tablename + " LIMIT 10;"
      print(statement)
      data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
      res = requests.post(url, params=data_dict)
      if res.status_code == 200:
        data = res.json()['results']
        data = json.dumps(data)
      else:
        return None
    print(data)
    return HttpResponse(data, content_type="application/json")

'''get entire database data and return the result'''
@csrf_exempt
def get_table_all(request):
  if request.is_ajax() and request.method == 'POST':
    connection_id = request.POST.get('connection_id', '')
    db = Connection.objects.get(id=int(connection_id))
    tables = Tablename.objects.filter(connection_id=int(connection_id))
    tables = list(tables)
    final_result = {}
    for table in tables:
      if db.is_mysql:
        try:
          connection = pymysql.connect(host=db.ip,
                                       port=db.port,
                                       user=db.username,
                                       password=db.password,
                                       db=db.dbname,
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor
                                       )
          with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM " + table.tablename + " LIMIT 10")
            data = cursor.fetchall()
        except:
          return None
      else:
        url = 'http://' + db.ip + ':' + str(db.port) + '/query/service'
        print(url)
        statement = 'use ' + db.dbname + ';'
        data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
        res = requests.post(url, params=data_dict)
        print(res.status_code)
        if res.status_code != 200:
          return None
        statement = "SELECT * FROM " + table.tablename + " LIMIT 10;"
        print(statement)
        data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
        res = requests.post(url, params=data_dict)
        if res.status_code == 200:
          data = res.json()['results']
        else:
          return None
      final_result[table.tablename] = data
    final_result = json.dumps(final_result)
    return HttpResponse(final_result, content_type="application/json")

'''view to delete an connection in connection list'''
def delete_connection(request):
  connection_id = request.GET.get('id')
  object = Connection.objects.get(id=connection_id)
  object.delete()
  return redirect('/task/connection_list', permanent=True)


class ConnectionListView(LoginRequiredMixin, ListView):
  model = Connection
  context_object_name = 'connection_list'
  template_name = 'task/connection_list.html'


class ConnectionDetailView(LoginRequiredMixin, DetailView):
  model = Connection
  context_object_name = 'connection'
  template_name = 'task/connection_detail.html'


def delete_connection_modal(request):
  connection_id = request.GET.get('id')
  object = Connection.objects.get(id=connection_id)
  object.delete()
  return redirect('/task/create_task', permanent=True)


class ConnectionListModalView(LoginRequiredMixin, ListView):
  model = Connection
  context_object_name = 'connection_list'
  template_name = 'task/connection_list_modal.html'


class ConnectionDetailModalView(LoginRequiredMixin, DetailView):
  model = Connection
  context_object_name = 'connection'
  template_name = 'task/connection_detail_modal.html'


class LoadDatabaseModalView(LoginRequiredMixin, FormView):
  model = Connection
  form_class = LoadDatabaseForm
  template_name = 'task/load_database_modal.html'
  success_url = '/task/load_database_success'
  fail_url = '/task/load_database_fail'


  def form_invalid(self, form):
    return render(request, self.fail_url)

  def form_valid(self, form):
    username = form.cleaned_data['Mysql Username']
    ip = form.cleaned_data['Mysql Host Address']
    dbname = form.cleaned_data['Mysql Database Name']
    password = form.cleaned_data['Mysql Password']
    port = form.cleaned_data['Mysql Port Number']
    a_ip = form.cleaned_data['AsterixDB Host Address']
    a_dbname = form.cleaned_data['AsterixDB Database Name']
    a_port = form.cleaned_data['AsterixDB Port Number']
    if a_ip != '':
      db = form.load_database_A(a_ip, a_dbname, a_port, self.request.user)
    elif ip != '':
      db = form.load_database(username, ip, password, dbname, port, self.request.user)
    else:
      db = None
    if not db:
      return self.form_invalid(form)
    return super(LoadDatabaseModalView, self).form_valid(form)


class LoadDatabaseSuccessModalView(LoginRequiredMixin, TemplateView):
  template_name = 'task/load_database_success_modal.html'


class LoadDatabaseFailModalView(LoginRequiredMixin, TemplateView):
  template_name = 'task/load_database_fail_modal.html'



class TaskListView(LoginRequiredMixin, ListView):
  model = Task
  template_name = 'task/task_list.html'

  def dispatch(self, request, *args, **kwargs):
    user = self.request.user
    self.array = []
    self.task_complete = False
    try:
      task_ids = Participation.objects.filter(labeler=user.email).values('task').distinct()
      get_list_or_404(task_ids)
      self.task_list = Task.objects.filter(id__in=task_ids)
      get_list_or_404(self.task_list)
    except:
        return redirect('/task/task_empty', permanent=True)
    for taskid in self.task_list:
      try:
        task_object = get_object_or_404(Task, pk=taskid.pk)
        post_response_ids = PostResponse.objects.filter(task=taskid.pk, responder=self.request.user.pk).values_list('post__id', flat=True).distinct()
        post_list = get_list_or_404(taskid.post_list.filter(~Q(id__in=post_response_ids)))
        if len(post_response_ids) >= int(Task.objects.filter(id=taskid.pk).values_list('num_posts', flat=True).first()):
          self.array.append(True)
        else:
          self.array.append(False)
      except:
        self.array.append(True)
    return super(TaskListView, self).dispatch(request, *args, **kwargs)

  def get_queryset(self):
    return self.task_list

  def get_context_data(self, **kwargs):
    context = super(TaskListView, self).get_context_data(**kwargs)
    context['task_list'] = self.get_queryset()
    context['task_complete_list'] = self.array
    return context

class TakeTaskView(LoginRequiredMixin, TemplateView):
  model = Task
  template_name = 'task/take_task.html'
  ctr = 1
  def dispatch(self, request, *args, **kwargs):
    self.task = get_object_or_404(Task, pk=self.kwargs['pk'])
    post_list = []
    temppost = ''
    post_response_ids = PostResponse.objects.filter(task=self.task.pk, responder=self.request.user.pk).values_list('post__id', flat=True).distinct()
    self.num_labeled = len(PostResponse.objects.filter(task=self.task.pk, responder=self.request.user.pk).values_list('responder__email', flat=True))
    self.num_posts = list(Task.objects.filter(id=self.task.pk).values_list('num_posts').first())[0]
    if int(self.num_labeled) / int(self.num_posts) * 100 > 100:
      self.scaled = 100
    else:
      self.scaled = int(self.num_labeled) / int(self.num_posts) * 100
    least_responded_post = Task.objects.filter(id=self.task.pk).values_list('num_labelers', flat=True).first()
    lst_reponded_list = []
    res_reponded_list = []
    try:
      temp = get_list_or_404(self.task.post_list.filter(~Q(id__in=post_response_ids)))      
      l1 = list(self.task.post_list.all().filter(task=self.task.pk).values_list('id', flat=True))
      l2 = list(post_response_ids)
      diff_list = [item for item in l1 if not item in l2]
      for responded_post in diff_list:
        responder_ids = list(PostResponse.objects.filter(task=self.task.pk, post=responded_post).values_list('responder__id', flat=True).distinct())
        lnt = len(responder_ids)
        lsts = int(least_responded_post)
        if lnt < lsts:
          post_list = Post.objects.filter(id=responded_post)
          lst_reponded_list.append(len(responder_ids) + 1)
          least_responded_post = min(lst_reponded_list)
          break
        else:
          lst_reponded_list.append(len(responder_ids))
          res_reponded_list.append(Post.objects.filter(id=responded_post))
      if post_list == []:
        post_list = res_reponded_list[lst_reponded_list.index(min(lst_reponded_list))]
      if not responded_post:
        post_list = temp
      self.post = post_list[0]
    except:
      return redirect('/task/task_complete', permanent=True)

    return super(TakeTaskView, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(TakeTaskView, self).get_context_data(**kwargs)
    context['task'] = self.task
    context['post'] = self.post
    context['label_list'] = self.task.label_list.all()
    context['post_list'] = self.task.post_list.all()
    context['num_labeled'] = self.num_labeled
    context['scaled'] = self.scaled
    return context

class TaskCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'task/task_complete.html'

class TaskEmptyView(LoginRequiredMixin, TemplateView):
    template_name = 'task/task_empty.html'

class LoadDatabaseView(LoginRequiredMixin, FormView):
  model = Connection
  error = {}
  form_class = LoadDatabaseForm
  template_name = 'task/load_database.html'
  success_url = '/task/load_database_success'
  fail_template = 'task/load_database_fail.html'

  def form_notvalid(self, form):
    print(self.error)
    return render(self.request, self.fail_template, self.error)

  def form_valid(self, form):
    error = None
    username = form.cleaned_data['Mysql Username']
    ip = form.cleaned_data['Mysql Host Address']
    dbname = form.cleaned_data['Mysql Database Name']
    password = form.cleaned_data['Mysql Password']
    port = form.cleaned_data['Mysql Port Number']
    a_ip = form.cleaned_data['AsterixDB Host Address']
    a_dbname = form.cleaned_data['AsterixDB Database Name']
    a_port = form.cleaned_data['AsterixDB Port Number']
    if a_ip != '':
        error, db = form.load_database_A(a_ip, a_dbname, a_port, self.request.user)
    elif ip != '':
        error, db = form.load_database(username, ip, password, dbname, port, self.request.user)
    else:
      db = None
      self.error = {'error': 'Empty IP found!'}
    if not db:
      if error:
        self.error = error
      return self.form_notvalid(form)
    return super(LoadDatabaseView, self).form_valid(form)


class LoadDatabaseSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'task/load_database_success.html'


class LoadDatabaseFailView(LoginRequiredMixin, TemplateView):
  template_name = 'task/load_database_fail.html'


class CreateTaskView(LoginRequiredMixin, FormView):
  model = Task
  form_class = CreateTaskForm
  template_name = 'task/create_task.html'
  success_url = '/task/create_task_success'

  def get_form_kwargs(self):
    kwargs = super(CreateTaskView, self).get_form_kwargs()
    kwargs.update({'user': self.request.user})
    return kwargs

  def form_valid(self, form):
    task_title = form.cleaned_data['Task Title']
    task_description = form.cleaned_data['Task Description']
    task_upload_file = form.cleaned_data['upload']
    post_name = form.cleaned_data['tablename_post']
    post_col_name = form.cleaned_data['colname_post']
    db_info = form.cleaned_data['connection']
    task_num_labelers = form.cleaned_data['Min number of labelers per post']
    task_num_posts = form.cleaned_data['Min number of posts that a labeler should complete']
    task_random_label = form.cleaned_data['Label Posts in Random Order']
    quiz_title = form.cleaned_data['Quiz Title']
    quiz_description = form.cleaned_data['Quiz Description']
    max_posts = form.cleaned_data['Number of Questions']
    pass_mark = form.cleaned_data['Pass Mark']
    participating_coders = form.cleaned_data['Participating Labelers']
    labels = form.cleaned_data['label']
    prerequisite = form.cleaned_data['Choose Quiz']
    readerR = csv.reader(TextIOWrapper(task_upload_file, errors='ignore'), delimiter='|', skipinitialspace=True)
    labels = next(readerR)
    posts = list(readerR)
    task_upload_file.seek(0)
    if 'Preview' in self.request.POST:
      context = {
          "task_title": task_title or"N/A",
          "task_description": task_description or"N/A",
          "task_num_labelers": task_num_labelers or"N/A",
          "task_num_posts": task_num_posts or"N/A",
          "quiz_title": quiz_title or"N/A",
          "quiz_description": quiz_description or"N/A",
          "task_random_label": "YES" if task_random_label else "NO",
          "max_posts": max_posts or"N/A",
          "pass_mark": pass_mark or"N/A",
          "participating_coders": participating_coders.split("\n"),
          "task_label": labels,
          "task_post": [x[0] for x in posts],
      }
      return render(self.request, 'task/preview_task.html', context)
    else:
      task = form.create_task(task_title, task_description, self.request.user, prerequisite, task_num_labelers, task_num_posts, task_random_label, task_upload_file, db_info, post_name, post_col_name, labels)
      form.send_email(task)
      return super(CreateTaskView, self).form_valid(form)


class CreateTaskSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'task/create_task_success.html'


'''main view to edit the task'''

class EditTaskView(LoginRequiredMixin, FormView):
  model = Task
  form_class = EditTaskForm
  template_name = 'task/edit_task.html'
  success_url = '/task/edit_task_success'

  def form_valid(self, form):
    task_title = form.cleaned_data['Task Title']
    task_description = form.cleaned_data['Task Description']
    task_upload_file = form.cleaned_data['Upload Task Posts and Labels']
    task_num_labelers = form.cleaned_data['Min Number of Labelers']
    task_num_posts = form.cleaned_data['Min Number of Posts']
    task_random_label = form.cleaned_data['Label Posts in Random Order']
    quiz_title = form.cleaned_data['Quiz Title']
    quiz_description = form.cleaned_data['Quiz Description']
    max_posts = form.cleaned_data['Number of Questions']
    pass_mark = form.cleaned_data['Pass Mark']
    quiz_upload_file = form.cleaned_data['Upload Quiz Posts and Labels']
    participating_coders = form.cleaned_data['Participating Labelers']
    prerequisite=form.cleaned_data['Choose Quiz']
    task = form.edit_task(task_title, task_description, self.request.user, prerequisite, task_num_labelers, task_num_posts, task_random_label, task_upload_file)
    form.send_email(task)
    return super(EditTaskView, self).form_valid(form)

class EditTaskSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'task/edit_task_success.html'


'''main view to update the labeler'''
class UpdateLabelerView(LoginRequiredMixin, FormView):
  model = Task
  form_class = UpdateLabelerForm
  template_name = 'task/update_labeler.html'
  success_url = '/task/update_labeler_success'
  def dispatch(self, request):
    if request.method == 'GET':
      self.argA = request.GET.get('pk')
      prime = UpdateLabelerForm(initial={'extra': 0, 'Select Task': request.GET.get('pk'), 'Task Id': request.GET.get('id'), 'Participating Labelers':request.GET.get('clist')})
      return render(request, 'task/update_labeler.html', {'form': prime})
    else:
      all_labelers = []
      for index in range(10):
        if request.POST.get('labeler_{index}'.format(index=index)):
          all_labelers.append(request.POST.get('labeler_{index}'.format(index=index)))
      if 'additem' in request.POST or 'removefield' in request.POST:
        form = UpdateLabelerForm(initial={'extra': request.POST.get('extra_field_count'), 'Select Task': request.POST.get('Select Task'), 'Task Id': request.POST.get('ID'), 'Participating Labelers':','.join(all_labelers)})
        return render(request, 'task/update_labeler.html', {'form': form})
      else:
        form = UpdateLabelerForm(request.POST)
        if form.is_valid():
          ttask = form.cleaned_data['Select Task']
          all_labelers = []
          for index in range(int(form.cleaned_data['extra_field_count'])):
            all_labelers.append(request.POST.get('labeler_{index}'.format(index=index)))
          tcoders = '\r\n'.join(all_labelers)
          task_id = form.cleaned_data['ID']
          delete_response = form.cleaned_data['Detele responses when removing labelers']    
          pform = form.update_labeler(ttask, tcoders, task_id, delete_response)
          return super(UpdateLabelerView, self).form_valid(pform)



class UpdateLabelerSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'task/update_labeler_success.html'


class TaskEvaluationListView(LoginRequiredMixin, ListView):
  model = Task
  template_name = 'task/task_evaluation_list.html'

  def dispatch(self, request, *args, **kwargs):
    self.task_list = Task.objects.filter(creator=self.request.user.pk)
    self.array = []
    t = []
    pt = []
    for task_name in self.task_list:
      row = []
      row.append(task_name)
      val = len(PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True))
      l = list(Task.objects.filter(title=task_name).values_list('num_posts').first())
      if l[0]:
        row.append(int(val) / int(l[0]))
        row.append(list(set([part.encode("utf8") for part in PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True)])))
        for l in list(set([part.encode("utf8") for part in PostResponse.objects.filter(task=task_name.pk).values_list('responder__email', flat=True)])):
          t.append(l)
      else:
        row.append(val)
      self.array.append(row)
    self.counter = Counter(t)
    pt.append(self.counter.keys())
    pt.append(self.counter.values())
    self.counter = pt
    try:
      self.task_size = len(self.task_list)
      get_list_or_404(self.task_list)
    except:
      return redirect('/task/task_evaluation_empty', permanent=True)

    return super(TaskEvaluationListView, self).dispatch(request, *args, **kwargs)

  def get_queryset(self):
    return self.task_list

  def get_context_data(self, **kwargs):
    context = super(TaskEvaluationListView, self).get_context_data(**kwargs)
    context['task_list'] = self.get_queryset()
    context['array'] = self.array
    context['counter'] = self.counter
    return context

class TaskEvaluationEmptyView(LoginRequiredMixin, TemplateView):
    template_name = 'task/task_evaluation_empty.html'

class TaskEvaluationDetailView(LoginRequiredMixin, DetailView):
  model = Task
  template_name = 'task/task_evaluation_detail.html'

  def dispatch(self, request, *args, **kwargs):
    self.task = get_object_or_404(Task, pk=self.kwargs['pk'])
    self.array = []
    self.kappa = []
    self.kappa1 = []
    self.kappa_name = "/media/kappa_" + str(self.task.title) + "_" + str(self.task.pk) + '.csv'
    self.eval_name = "/media/eval_" + str(self.task.title) + "_" + str(self.task.pk) + '.csv'
    self.kappa_nameLong = self.kappa_name
    self.lblr = []
    self.head = []
    self.coder_emails = PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinct().order_by('responder__email')
    post_list = self.task.post_list.all()
    media_root = '/var/www/media/'
    kappa_path = media_root + 'kappa_' + str(self.task.title) + "_" + str(self.task.pk) + '.csv'
    eval_path = media_root + 'eval_' + str(self.task.title) + "_" + str(self.task.pk) + '.csv'
    if os.path.exists(kappa_path):
      os.remove(kappa_path)
    if os.path.exists(eval_path):
      os.remove(eval_path)
    name = eval_path
    filepp = open(str(name),"w+")
    filepp.write(',')
    for coder_email in self.coder_emails:
      filepp.write(coder_email)
      filepp.write(',')
    filepp.write('Majority Vote')
    filepp.write('\n')
    voteList = {}
    listTemp = []
    cpr = 0
    for post in post_list:
      row = []
      cpr = cpr + 1
      row.append(post.content)
      filepp.write(post.content)
      filepp.write(',')
      i = 0
      if len(self.coder_emails) > 5:
        self.coder_emails_temp = self.coder_emails[0:5]
        temp_emails = self.coder_emails
        self.coder_emails_temp.append("(List continues...)")
        voteList = {}
        listTemp = []
        for coder_email in temp_emails:
          label = 'N/A'
          try:
            post_response = PostResponse.objects.filter(task=self.task.pk, post=post.pk, responder__email=coder_email).last()
            label = post_response.label
            filepp.write(str(label))
            listTemp.append(str(label))
            filepp.write(',')
          except:
            filepp.write('N/A') 
            listTemp.append('N/A')
            filepp.write(',')
            pass
        maximum = ('', 0)
        for n in listTemp:
          if n in voteList:
            voteList[n] += 1
          else:
            voteList[n] = 1
          if voteList[n] > maximum[1]:
             maximum = (n, voteList[n])
      else:
        self.coder_emails_temp = self.coder_emails
        voteList = {}
        listTemp = []
      i = 0
      for coder_email in self.coder_emails_temp:
        if len(self.coder_emails) > 5 and coder_email == "(List continues...)":
           label = '...'
        else:
           label = 'N/A'
           try:
             post_response = PostResponse.objects.filter(task=self.task.pk, post=post.pk, responder__email=coder_email).last()
             label = post_response.label
             if len(self.coder_emails) <= 5:
                filepp.write(str(label))
                filepp.write(',')
             listTemp.append(str(label))
           except:
             if len(self.coder_emails) <= 5:
                filepp.write('N/A')
                filepp.write(',')
             listTemp.append(str(label))
             pass
        row.append(label)
      maximum = ('', 0)
      for n in listTemp:
        if n in voteList:
          voteList[n] += 1
        else:
          voteList[n] = 1
        if voteList[n] > maximum[1]:
          maximum = (n, voteList[n])
      filepp.write(maximum[0])
      filepp.write('\n')
      maximum = ('', 0)
      for n in listTemp:
        if n in voteList:
          voteList[n] += 1
        else:
          voteList[n] = 1
        if voteList[n] > maximum[1]:
          maximum = (n, voteList[n])
      row.append(maximum[0])
      self.array.append(row)
    try:
      annotation_triplet_list = []
      post_response_list = PostResponse.objects.filter(task=self.task.pk)
      post_response_t = [part.encode("utf8") for part in PostResponse.objects.filter(task=self.task.pk).values_list('responder__email', flat=True).distinct()]
      lst_rp = []
      triple_list = []
      ctr = 0
      if len(post_response_t) > 5:
        post_response_t_temp = post_response_t[0:5]
        for post_response in post_response_t_temp:
          post_response = str(post_response).replace('b\'', '')
          post_response = post_response.replace('\'', '')
          lst_rp.append(post_response)
        lst_rp.append("(List continues...)")
        comb_temp = combinations(post_response_t, 2)
        annotation_triplet_list_all = []
        for i in list(comb_temp):
          annotation_triplet_list = []
          ip = []
          sp = ""
          temp = str(i[0]).replace('b\'', '')
          temp = temp.replace('\'', '')
          if ([temp, temp, '1.0'] not in triple_list):
            triple_list.append([])
            triple_list[ctr].append(temp)
            triple_list[ctr].append(temp)
            triple_list[ctr].append('1.0')
            ctr = ctr + 1
          triple_list.append([])
          for s in i:
            st = str(s).replace('b\'', '')
            st = st.replace('\'', '')
            ip.append(st)
          for post_response in post_response_list:
            if (post_response.responder.email in ip):
              annotation_triplet = (post_response.responder.email, post_response.post.content, post_response.label.content)
              annotation_triplet_list.append(annotation_triplet)
              annotation_triplet_list_all.append(annotation_triplet)
          t = AnnotationTask(annotation_triplet_list)
          triple_list[ctr].append(str(t.kappa()))
          self.lblr.append(triple_list)
          ctr = ctr + 1
        t = AnnotationTask(annotation_triplet_list_all)
        self.alpha1 = t.alpha()
        self.kappa1.append(triple_list)
        name = kappa_path
        filep = open(str(name), "w+")
        i = 0
        ct = 1
        filep.write(',')
        prev_email = 's'
        for email in triple_list:
          if email[0] != prev_email:
            prev_email = email[0]
            filep.write(email[0])
            filep.write(',')
        filep.write(email[1])
        filep.write('\n')
        for row in triple_list:
          if i == 0 or i == ct - 1:
            filep.write(row[0])
            filep.write(',')
            for k in range(0, i):
              filep.write('--,')
          if i == len(self.coder_emails) - 1:
            i = ct
            filep.write(row[2])
            filep.write('\n')
            ct = ct + 1
          else:
            i = i + 1
            filep.write(row[2])
            filep.write(',')
        filep.close()
      else:
        post_response_t_temp = post_response_t
        for post_response in post_response_t_temp:
          post_response = str(post_response).replace('b\'', '')
          post_response = post_response.replace('\'', '')
          lst_rp.append(post_response)

      self.head.append(lst_rp)
      comb = combinations(post_response_t_temp, 2)
      ip = []
      lst_rp = []
      triple_list = []
      ctr = 0
      annotation_triplet_list_all = []
      for i in list(comb):
        annotation_triplet_list = []
        ip = []
        sp = ""
        temp = str(i[0]).replace('b\'', '')
        temp = temp.replace('\'', '')
        if ([temp, temp, '1.0'] not in triple_list):
          triple_list.append([])
          triple_list[ctr].append(temp)
          triple_list[ctr].append(temp)
          triple_list[ctr].append('1.0')
          ctr = ctr + 1
        triple_list.append([])
        for s in i:
          st = str(s).replace('b\'', '')
          st = st.replace('\'', '')
          ip.append(st)
          triple_list[ctr].append(st)
        for post_response in post_response_list:
          if (post_response.responder.email in ip):
            annotation_triplet = (post_response.responder.email, post_response.post.content, post_response.label.content)     
            annotation_triplet_list.append(annotation_triplet)
            annotation_triplet_list_all.append(annotation_triplet)
        t = AnnotationTask(annotation_triplet_list)
        triple_list[ctr].append(str(t.kappa()))
        self.lblr.append(triple_list)
        ctr = ctr + 1
      t = AnnotationTask(annotation_triplet_list_all)
      if len(post_response_t) > 5:
        self.alpha = self.alpha1
      else:
        self.alpha = t.alpha()
      print (triple_list)
      temp = self.head[0][-1]
      triple_list_final = list(triple_list)
      if ([temp, temp, '1.0'] not in triple_list_final):
        triple_list_final.append([])
        triple_list_final[ctr].append(temp)
        triple_list_final[ctr].append(temp)
        triple_list_final[ctr].append('1.0')
      self.kappa.append(triple_list_final)
      name = kappa_path
      filep = open(str(name),"w+")
      i = 0
      ct = 1
      filep.write(',')
      prev_email = 's'
      for email in triple_list:
        if email[0] != prev_email:
          prev_email = email[0]
          filep.write(email[0])
          filep.write(',')
      filep.write(email[1])
      filep.write('\n')
      for row in triple_list:
        if i == 0 or i == ct - 1:
          filep.write(row[0])
          filep.write(',')
          for k in range(0, i):
            filep.write('--,')
        if i == len(self.coder_emails) - 1:
          i = ct
          filep.write(row[2])
          filep.write('\n')
          ct = ct + 1
        else:
          i = i + 1
          filep.write(row[2])
          filep.write(',')
      filep.write(triple_list[-1][1] + ',--' * (len(self.coder_emails) - 1) + ',1.0' + '\n')
      filep.close()
    except:
      self.alpha = 'N/A'
      name = kappa_path
      filep = open(str(name), "w+")

    return super(TaskEvaluationDetailView, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(TaskEvaluationDetailView, self).get_context_data(**kwargs)
    context['task'] = self.task
    context['array'] = self.array
    context['coder_email_list'] = self.coder_emails_temp
    context['alpha'] = self.alpha
    context['kappa'] = self.kappa
    context['head'] = self.head
    context['tablefile1'] = self.eval_name
    if self.kappa_nameLong != self.kappa_name:
      self.kappa_name = self.kappa_nameLong
    context['tablefile'] = self.kappa_name
    return context

  def exportCSV(triple_list, alpha1, coder_emails):
    with open('csvfile.csv', 'wb') as file:
      for email in coder_emails:
        print (email)
        file.write('email...')
        file.write('\n')
    for row in coder_emails:
      for col in row:
        file.write(col)
      for rowp in triple_list[0]:
        if forloop.counter != forloop.parentloop.counter:
          if col in rowp:
            file.write(rowp[2])

class TaskParticipationListView(LoginRequiredMixin, ListView):
  model = Participation
  template_name = 'task/task_participation_list.html'

  def dispatch(self, request, *args, **kwargs):
    self.task_list = Task.objects.filter(creator=self.request.user.pk)
    self.array = []
    for task_name in self.task_list:
      row = []
      x = Participation.objects.filter(task=task_name.pk).values('id').distinct('task');
      responded_posts = len(PostResponse.objects.filter(task=task_name.pk))
      posts_no = len(Task.objects.filter(id=task_name.pk).values_list('post_list', flat=True))
      row.append(task_name)
      self.labeler_list = [part.encode("utf8") for part in Participation.objects.filter(task=task_name.pk).values_list('labeler', flat=True)]
      row.append(list(self.labeler_list))
      self.array.append(row)
    try:
      get_list_or_404(self.task_list)
    except:
      return redirect('/task/task_participation_empty', permanent=True)

    return super(TaskParticipationListView, self).dispatch(request, *args, **kwargs)

  def get_queryset(self):
    return self.task_list

  def get_context_data(self, **kwargs):
    context = super(TaskParticipationListView, self).get_context_data(**kwargs)
    context['array'] = self.array
    return context

class TaskParticipationEmptyView(LoginRequiredMixin, TemplateView):
    template_name = 'task/task_participation_empty.html'
