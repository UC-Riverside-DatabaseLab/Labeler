from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.urlresolvers import resolve
import requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import MultiWidgetField, Layout, Field, Submit, Fieldset, ButtonHolder, HTML, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from django.forms.fields import ChoiceField
from django.conf import settings
import random
import string
import hashlib
import json
from .models import Classify
from quiz.models import Quiz
from response.models import PostResponse
from task.models import Task
from collections import deque
import os
import csv
from io import TextIOWrapper

CHOICES = (('T', 'True',), ('F', 'False',))
VEC_CHOICES = (("count", "count"), ("tfidf", "tfidf"),)
CLA_CHOICES = (("cnn", "cnn"), ("rf", "rf"), ("svm", "svm"))

class CreateClassificationModelForm(forms.Form):

  def __init__(self, *args, **kwargs):
    super(CreateClassificationModelForm, self).__init__(*args, **kwargs)
    self.conf_url = "http://localhost:6666/configure"
    self.train_url = "http://localhost:6666/train"
    self.headers = {'content-type': 'application/json'}
    self.fields['Classifier Name'] = forms.CharField(max_length=50)
    self.fields['Classifier Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Upload Task Posts and Labels'] = forms.FileField(required=False)
    self.fields['Vectorizer'] = forms.CharField(max_length=50, widget=forms.Select(choices=VEC_CHOICES))
    self.fields['Classifier'] = forms.CharField(max_length=50, widget=forms.Select(choices=CLA_CHOICES))

    self.fields['dev_sample_percentage'] = forms.FloatField(initial=0.1, required=False)
    self.fields['embedding_dim'] = forms.IntegerField(initial=128, required=False)
    self.fields['filter_sizes'] = forms.CharField(initial="3,4,5", max_length=50, required=False)
    self.fields['num_filters'] = forms.IntegerField(initial=128, required=False)
    self.fields['dropout_keep_prob'] = forms.FloatField(initial=0.5, required=False)
    self.fields['l2_reg_lambda'] = forms.FloatField(initial=0.0001, required=False)
    self.fields['batch_size'] = forms.IntegerField(initial=64, required=False)
    self.fields['num_epochs'] = forms.IntegerField(initial=200, required=False)
    self.fields['evaluate_every'] = forms.IntegerField(initial=100, required=False)
    self.fields['checkpoint_every'] = forms.IntegerField(initial=100, required=False)
    self.fields['num_checkpoints'] = forms.IntegerField(initial=5, required=False)
    self.fields['allow_soft_placement'] = forms.CharField(initial='T', max_length=50, widget=forms.Select(choices=CHOICES), required=False)
    self.fields['log_device_placement'] = forms.CharField(initial='T', max_length=50, widget=forms.Select(choices=CHOICES), required=False)
    self.fields['random_state'] = forms.IntegerField(initial=10, required=False)

    self.cnn_conf = ['dev_sample_percentage', 'embedding_dim', 'filter_sizes', 'num_filters',
      'dropout_keep_prob', 'l2_reg_lambda', 'batch_size', 'num_epochs', 'evaluate_every', 'checkpoint_every', 
      'num_checkpoints', 'allow_soft_placement', 'log_device_placement', 'random_state']
    task_name_list = Task.objects.all()
    temp = []
    for task_name in task_name_list:
      post_ll = Task.objects.filter(id=task_name.pk).values_list('post_list', flat=True)
      count = 0
      for postid in post_ll:
        if len(PostResponse.objects.filter(task=task_name, post=postid).values_list('responder__email', flat=True).distinct()) >= int(Task.objects.filter(id=task_name.pk).values_list('num_labelers', flat=True).first()):
          count = count + 1
      if count == len(post_ll):
        temp.append(task_name.pk)
    self.fields['Choose Labeling Task'] = forms.ModelChoiceField(queryset=Task.objects.filter(id__in=temp), required=False)
    self.helper = FormHelper()
    self.helper.form_id = 'create_classification_model_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/classify/create_classification_model/'
    self.helper.layout = Layout(
      HTML("""<script>
        $(document).ready(
          function() {
          $("#id_Classifier").change(function()
          {
            console.log($('#id_Classifier').val());
            if ($('#id_Classifier').val() === "cnn")
            {
              $('#cnn_conf').show();
            }
            else
            {
              $('#cnn_conf').hide();
            }
          });
          });
          </script>
      """),
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 1: Create Classification Model
          </div>
          <div class="panel-body">
          """),
      Field('Classifier Name', placeholder="Enter the classification task name..."),
      Field('Classifier Description', placeholder="Write some description about the classifier..."),
      HTML("""
      <!--script>$(function() {
          $('input[name=post-format]').on('click init-post-format', function() {
              $('#gallery-box').toggle($('#post-format-gallery').prop('checked'));
          }).trigger('init-post-format');
         $('input[name=post-format]').on('click init-post-format', function() {
        $('#gallery-box1').toggle($('#post-format-gallery1').prop('checked'));
          }).trigger('init-post-format');

      });
      </script-->

      <!--label><input type="radio" name="post-format" id="post-format-gallery">CSV File</label><br/>
      <label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label-->

      <!--div id="gallery-box"> <!--style="border: 1px solid red;"--><!--select class="some_class">
                <option value="1">Sum</option>
                  <option value="2">Difference</option>
                <option value="3">Whatever</option>
            </select-->"""),
      HTML("""
                        </div>"""),
      HTML("""
      <!--div id="gallery-box1"> <!--style="border: 1px solid red;"--><!--select class="some_class" id="test"-->
      <!--script-->"""),
      HTML("""</div>"""),
      HTML("""<style> p.solid {border : 1px; display: inline-block ; border-style: solid;} </style>
      <!--table style="border: 1px solid black;"-->

      <tr>
      <td>
      <!--p class="solid">
        <b>Note</b> : Upload a csv file with <a href="/media/sample_survey1.csv" download="sample_survey1.csv">this sample format</a> <br/>[All labels separated with pipelines on the first line. <br/>Each post on a separate line after that.]
        </td>
      </tr>
      </p-->
        <!--/table-->
      """),
      HTML("""</div-->
          </div-->"""),
      HTML("""<div class="panel panel-info">
                                        <div class="panel-heading">
                                                Step 2: Source of Training Data
                                        </div>
                                        <div class="panel-body"> """),
      HTML("""
                        <script>$(function() {
                            $('input[name=post-format]').on('click init-post-format', function() {
                                $('#gallery-box').toggle($('#post-format-gallery').prop('checked'));
                            }).trigger('init-post-format');
                                 $('input[name=post-format]').on('click init-post-format', function() {
                                $('#gallery-box1').toggle($('#post-format-gallery1').prop('checked'));
                            }).trigger('init-post-format');

                        });
                        </script>

                        <label><input type="radio" name="post-format" id="post-format-gallery">CSV File</label><div></div>
                        <!--label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label-->

                        <div id="gallery-box"> <!--style="border: 1px solid red;"--><!--select class="some_class">
                            <option value="1">Sum</option>
                                <option value="2">Difference</option>
                            <option value="3">Whatever</option>
                        </select-->                        <!--label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label-->
"""),

      Field('Upload Task Posts and Labels', placeholder = ""),
      HTML("""</div><div>"""),
      HTML("""<label><input type="radio" name="post-format" id="post-format-gallery1">Labeling Task</label>
                        </div><div id="gallery-box1"> <!--style="border: 1px solid red;"--><!--select class="some_class" id="test"-->
                        <!--script-->"""),
      Field('Choose Labeling Task', placeholder=""),
      HTML(""" <!--label><input type="radio" name="post-format" id="post-format-gallery1">CSV File</label--><div></div>                                            
                        </div>"""),
      HTML("""</div></div>"""),
            HTML("""<div class="panel panel-info">
                                        <div class="panel-heading">
                                                Step 3: Configuration
                                        </div>
                                        <div class="panel-body"> """),

      Field('Vectorizer', placeholder = ""),
      Field('Classifier', placeholder = ""),
      Fieldset("Configurations for cnn classifier",
          MultiWidgetField(*self.cnn_conf, attrs=({'style': 'width: 30%; display: inline-block;'})),
          id = 'cnn_conf'
      ),
      HTML("""</div></div>"""),
    )
    self.helper.add_input(Submit('create_classification_model_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))
  
  def get_path(self, user, folder):
    return os.path.join(settings.MEDIA_ROOT, 'models', user, folder)

  def create_classification_model(self, classifier_name, classifier_description, user, task_upload_file, task, vectorizer, classifier, conf_dict):

    model_path = self.get_path(str(user), classifier_name)
    print(model_path)
    if not os.path.exists(model_path):
      os.makedirs(model_path)
    if task_upload_file:
      reader = csv.reader(TextIOWrapper(task_upload_file), skipinitialspace=True)
      next(reader)
      posts = []
      labels = []
      for line in reader:
        posts.append(line[0])
        labels.append(line[-1])


    
    conf_dict["vectorizer"] = vectorizer
    conf_dict["classifier"] = classifier
    response = requests.post(self.conf_url, data=json.dumps(conf_dict), headers=self.headers)
    if json.loads(response.text)["result"]:
      print('dasda')
    """
    classify_obj = Classify.objects.create(
                                name=classifier_name,
                                description=classifier_description,
                                creator=user,
                                task=task,
                                upload_task=task_upload_file,
                                vectorizer=vectorizer,
                                classifier=classifier,
                                conf=json.dumps(conf_dict)
                                )
    classify_obj.save()
    self.id = classify_obj.id
    return classify_obj
    """