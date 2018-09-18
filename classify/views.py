from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, FormView, DetailView, DeleteView
from .models import Classify
from task.models import Task
import background_task.models as bgmodel
import background_task.models_completed as bgmodel_c
from collections import deque
from collections import Counter
from .forms import CreateClassificationModelForm, ClassifyDataForm
from flask import Flask, request
import re
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib import messages
import random
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class CreateClassificationModelView(LoginRequiredMixin, FormView):
  model = Classify
  form_class = CreateClassificationModelForm

  template_name = 'classify/create_classification_model.html'
  success_url = '/classify/create_classification_model_success'

  def form_valid(self, form):
    cnn_conf = ['word_embedding', 'dev_sample_percentage', 'embedding_dim', 'filter_sizes', 'num_filters',
      'dropout_keep_prob', 'l2_reg_lambda', 'batch_size', 'num_epochs', 'evaluate_every', 'checkpoint_every', 
      'num_checkpoints', 'allow_soft_placement', 'log_device_placement', 'cnn_random_state']
    rf_conf = ['max_depth', 'n_estimators', 'criterion', 'min_samples_split', 'min_samples_leaf',
      'max_features', 'max_leaf_nodes', 'min_impurity_decrease', 'min_impurity_split', 'rf_random_state',
      'rf_class_weight', 'bootstrap', 'oob_score', 'warm_start']
    svm_conf = ['C', 'kernel', 'degree', 'gamma', 'coef0', 'shrinking', 'tol',
      'cache_size', 'svm_class_weight', 'max_iter', 'decision_function_shape', 'svm_random_state']
    classifier_name = form.cleaned_data['Classifier Name']
    classifier_description = form.cleaned_data['Classifier Description']
    task_upload_file = form.cleaned_data['Upload Task Posts and Labels']
    vectorizer = form.cleaned_data['Vectorizer']
    classifier = form.cleaned_data['Classifier']
    if classifier == 'cnn':
      conf_dict = {key: form.cleaned_data[key] for key in cnn_conf}
    elif classifier == 'rf':
      conf_dict = {key: form.cleaned_data[key] for key in rf_conf}
    elif classifier == 'svm':
      conf_dict = {key: form.cleaned_data[key] for key in svm_conf}
    else:
      conf_dict = None
    task = form.cleaned_data['Choose Labeling Task']
    form.create_classification_model(classifier_name, classifier_description, self.request.user, task_upload_file, task, vectorizer, classifier, conf_dict)
    return super(CreateClassificationModelView, self).form_valid(form)


class CreateClassificationModelSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'classify/create_classification_model_success.html'


class ClassifyDataView(LoginRequiredMixin, FormView):
  model = Classify
  form_class = ClassifyDataForm

  template_name = 'classify/classify_data.html'
  success_url = 'classify/classify_success.html'
  def form_valid(self, form):
    classifier = form.cleaned_data['Classifier']
    task_upload_file = form.cleaned_data['Upload Posts']
    classify = form.classify_data(classifier, task_upload_file, self.request.user)
    print(classify)
    return render(self.request, self.success_url, classify)

class ClassifySuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'classify/classify_success.html'


class ClassifyTaskListView(LoginRequiredMixin, ListView):
  context_object_name = 'classify_list'
  template_name = 'classify/classify_list.html'
  model = Classify

  def get_context_data(self, **kwargs):
    user_id = str(self.request.user.id) + '|'
    context = super(ClassifyTaskListView, self).get_context_data(**kwargs)
    context['running'] = bgmodel.Task.objects.all().filter(verbose_name__startswith=user_id)
    context['complete'] = bgmodel_c.CompletedTask.objects.all().filter(verbose_name__startswith=user_id)
    name_array = []
    for task in context['running']:
      value = task.verbose_name.replace(user_id, '')
      start_running = False
      if timezone.now() > task.run_at:
        start_running = True
      name_array.append((task, value, start_running))
    context['running_array'] = name_array
    name_array = []
    for task in context['complete']:
      value = task.verbose_name.replace(user_id, '')
      name_array.append((task, value))
    context['complete_array'] = name_array
    
    return context

class DeleteClassifyView(SuccessMessageMixin, DeleteView):
  model = bgmodel_c.CompletedTask
  success_url = '/classify/classify_list'
  template_name = 'classify/classify_delete.html'
  success_message = "deleted..."

  def DeleteClassifyView(self, request, *args, **kwargs):
    self.object = self.get_object()
    name = self.object.task_name
    request.session['name'] = name
    message = request.session['name'] + ' deleted successfully'
    messages.success(self.request, message)
    return super(DeleteView, self).delete(request, *args, **kwargs)
