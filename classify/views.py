from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, FormView, DetailView
from .models import Classify
from task.models import Task
from collections import deque
from collections import Counter
from .forms import CreateClassificationModelForm
from flask import Flask, request

from nltk.metrics.agreement import AnnotationTask

from itertools import combinations

import csv
import datetime
import os
from django.conf import settings
from django.views.decorators.http import require_POST

import random
from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

class CreateClassificationModelView(LoginRequiredMixin, FormView):
  model = Classify
  form_class = CreateClassificationModelForm

  template_name = 'classify/create_classification_model.html'
  success_url = '/classify/create_classification_model_success'
  def form_valid(self, form):
    self.cnn_conf = ['dev_sample_percentage', 'embedding_dim', 'filter_sizes', 'num_filters',
      'dropout_keep_prob', 'l2_reg_lambda', 'batch_size', 'num_epochs', 'evaluate_every', 'checkpoint_every', 
      'num_checkpoints', 'allow_soft_placement', 'log_device_placement', 'random_state']
    classifier_name = form.cleaned_data['Classifier Name']
    classifier_description = form.cleaned_data['Classifier Description']
    task_upload_file = form.cleaned_data['Upload Task Posts and Labels']
    vectorizer = form.cleaned_data['Vectorizer']
    classifier = form.cleaned_data['Classifier']
    if classifier == 'cnn':
      conf_dict = {key: form.cleaned_data[key] for key in self.cnn_conf}
    self.temp = Task.objects.filter(creator='1')
    task = form.cleaned_data['Choose Labeling Task']
    classify = form.create_classification_model(classifier_name, classifier_description, self.request.user, task_upload_file, task, vectorizer, classifier, conf_dict)
    return super(CreateClassificationModelView, self).form_valid(form)

  def get_conext(self, **kwargs):
    context['temp'] = self.temp
    return context


class CreateClassificationModelSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'classify/create_classification_model_success.html'