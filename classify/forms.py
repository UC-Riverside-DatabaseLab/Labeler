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
from .tasks import query_api

CHOICES = (('T', 'True',), ('F', 'False',))
VEC_CHOICES = (("count", "count"), ("tfidf", "tfidf"),)
CLA_CHOICES = (("cnn", "cnn"), ("rf", "rf"), ("svm", "svm"))
CRE_CHOICES = (('gini', 'gini'), ('entropy', 'entropy'))
DEC_CHOICES = (('ovo', 'ovo'), ('ovr', 'ovr'))
KER_CHOICES = (('rbf', 'rbf'), ('linear', 'linear'), ('poly', 'poly'), ('sigmoid', 'sigmoid'), ('precomputed', 'precomputed'))
WOR_CHOICES = (('None', 'None'), ('word2vec', 'word2vec'), ('glove', 'glove'), ('fasttext', 'fasttext'))
def get_path(user, folder):
  return os.path.join(settings.MEDIA_ROOT, 'models', user, folder)

class CreateClassificationModelForm(forms.Form):

  def __init__(self, *args, **kwargs):
    super(CreateClassificationModelForm, self).__init__(*args, **kwargs)
    self.train_url = "http://localhost:6666/train"
    self.headers = {'content-type': 'application/json'}
    self.fields['Classifier Name'] = forms.CharField(max_length=50)
    self.fields['Classifier Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Upload Task Posts and Labels'] = forms.FileField(required=False)
    self.fields['Vectorizer'] = forms.CharField(max_length=50, help_text='Method to translate post into a vector', widget=forms.Select(choices=VEC_CHOICES))
    self.fields['Classifier'] = forms.CharField(max_length=50, help_text='Type of classifier to use. If cnn is choosen, the vectorizer will be ignored and word_embeding will be used for vectorization',widget=forms.Select(choices=CLA_CHOICES))

    # fields for cnn
    self.fields['dev_sample_percentage'] = forms.FloatField(initial=0.2, required=False, help_text='Percentage of the training data to use for validation')
    self.fields['embedding_dim'] = forms.IntegerField(initial=10, required=False, help_text='Dimensionality of character embedding')
    self.fields['filter_sizes'] = forms.CharField(initial="3,3,3", max_length=50, required=False, help_text='Comma-separated filter sizes')
    self.fields['num_filters'] = forms.IntegerField(initial=16, required=False, help_text='Number of filters per filter size')
    self.fields['dropout_keep_prob'] = forms.FloatField(initial=0.5, required=False, help_text='Dropout keep probability')
    self.fields['l2_reg_lambda'] = forms.FloatField(initial=0.0001, required=False, help_text='L2 regularization lambda')
    self.fields['batch_size'] = forms.IntegerField(initial=2, required=False, help_text='Batch Size')
    self.fields['num_epochs'] = forms.IntegerField(initial=200, required=False, help_text='Number of training epochs')
    self.fields['evaluate_every'] = forms.IntegerField(initial=100, required=False, help_text='Evaluate model on dev set after this many steps')
    self.fields['checkpoint_every'] = forms.IntegerField(initial=100, required=False, help_text='Save model after this many steps')
    self.fields['num_checkpoints'] = forms.IntegerField(initial=2, required=False, help_text='Number of checkpoints to store')
    self.fields['allow_soft_placement'] = forms.CharField(initial='F', max_length=50, widget=forms.Select(choices=CHOICES), required=False, help_text='Allow device soft device placement')
    self.fields['log_device_placement'] = forms.CharField(initial='F', max_length=50, widget=forms.Select(choices=CHOICES), required=False, help_text='Log placement of ops on devices')
    self.fields['cnn_random_state'] = forms.IntegerField(initial=10, required=False, help_text='The seed used by the random number generator')
    self.fields['word_embedding'] = forms.CharField(initial='None', max_length=50, widget=forms.Select(choices=WOR_CHOICES), required=False, help_text='Source of word embedding to use')

    # fields for rf
    self.fields['max_depth'] = forms.CharField(initial='None', max_length=50, required=False, help_text='The maximum depth of the tree. If None, then nodes are expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.')
    self.fields['n_estimators'] = forms.IntegerField(initial=10, required=False, help_text='The number of trees in the forest.')
    self.fields['criterion'] = forms.CharField(initial="gini", max_length=50, widget=forms.Select(choices=CRE_CHOICES), required=False, help_text='The function to measure the quality of a split. Supported criteria are “gini” for the Gini impurity and “entropy” for the information gain.')
    self.fields['min_samples_split'] = forms.IntegerField(initial=2, required=False, help_text='The minimum number of samples required to split an internal node.')
    self.fields['min_samples_leaf'] = forms.IntegerField(initial=1, required=False, help_text='The minimum number of samples required to be at a leaf node.')
    self.fields['max_features'] = forms.CharField(initial='auto', max_length=50, required=False, help_text='The number of features to consider when looking for the best split')
    self.fields['max_leaf_nodes'] = forms.CharField(initial='None', max_length=50, required=False, help_text='Grow trees with max_leaf_nodes in best-first fashion.')
    self.fields['min_impurity_decrease'] = forms.FloatField(initial=0, required=False, help_text='A node will be split if this split induces a decrease of the impurity greater than or equal to this value.')
    self.fields['min_impurity_split'] = forms.CharField(initial='None', max_length=50, required=False, help_text='Threshold for early stopping in tree growth. A node will split if its impurity is above the threshold, otherwise it is a leaf.')
    self.fields['rf_random_state'] = forms.CharField(initial='None', max_length=50, required=False, help_text='The seed used by the random number generator')
    self.fields['rf_class_weight'] = forms.CharField(initial='None', max_length=50, required=False, help_text='Weights associated with classes in the form')
    self.fields['bootstrap'] = forms.CharField(initial='T', max_length=50, widget=forms.Select(choices=CHOICES), required=False, help_text='Whether bootstrap samples are used when building trees.')
    self.fields['oob_score'] = forms.CharField(initial='F', max_length=50, widget=forms.Select(choices=CHOICES), required=False, help_text='Whether to use out-of-bag samples to estimate the generalization accuracy.')
    self.fields['warm_start'] = forms.CharField(initial='F', max_length=50, widget=forms.Select(choices=CHOICES), required=False, help_text='When set to True, reuse the solution of the previous call to fit and add more estimators to the ensemble, otherwise, just fit a whole new forest.')
    
    # fields for svm
    self.fields['C'] = forms.FloatField(initial=1.0, required=False, help_text='Penalty parameter C of the error term.')
    self.fields['kernel'] = forms.CharField(initial='T', max_length=50, widget=forms.Select(choices=KER_CHOICES), required=False, help_text='Specifies the kernel type to be used in the algorithm.')
    self.fields['degree'] = forms.IntegerField(initial=3, required=False, help_text='Degree of the polynomial kernel function (‘poly’). Ignored by all other kernels.')
    self.fields['gamma'] = forms.CharField(initial='auto', max_length=50, required=False, help_text='Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’.')
    self.fields['coef0'] = forms.FloatField(initial=0, required=False, help_text='Independent term in kernel function. It is only significant in ‘poly’ and ‘sigmoid’.')
    self.fields['shrinking'] = forms.CharField(initial='T', max_length=50, widget=forms.Select(choices=CHOICES), required=False, help_text='Whether to use the shrinking heuristic.')
    self.fields['tol'] = forms.FloatField(initial=0.001, required=False, help_text='Tolerance for stopping criterion.')
    self.fields['cache_size'] = forms.FloatField(initial=200, required=False, help_text='pecify the size of the kernel cache (in MB).')
    self.fields['svm_class_weight'] = forms.CharField(initial='None', max_length=50, required=False, help_text='Set the parameter C of class i to class_weight[i]*C for SVC.')
    self.fields['max_iter'] = forms.IntegerField(initial=-1, required=False, help_text='Hard limit on iterations within solver, or -1 for no limit.')
    self.fields['decision_function_shape'] = forms.CharField(initial='ovr', max_length=50, widget=forms.Select(choices=DEC_CHOICES), required=False, help_text='Whether to return a one-vs-rest (‘ovr’) decision function as all other classifiers, or the original one-vs-one (‘ovo’) decision function of libsvm')
    self.fields['svm_random_state'] = forms.CharField(initial='None', max_length=50, required=False, help_text='The seed of the pseudo random number generator to use when shuffling the data')

    self.cnn_conf = ['word_embedding', 'dev_sample_percentage', 'embedding_dim', 'filter_sizes', 'num_filters',
      'dropout_keep_prob', 'l2_reg_lambda', 'batch_size', 'num_epochs', 'evaluate_every', 'checkpoint_every', 
      'num_checkpoints', 'allow_soft_placement', 'log_device_placement', 'cnn_random_state']
    self.rf_conf = ['max_depth', 'n_estimators', 'criterion', 'min_samples_split', 'min_samples_leaf',
      'max_features', 'max_leaf_nodes', 'min_impurity_decrease', 'min_impurity_split', 'rf_random_state',
      'rf_class_weight', 'bootstrap', 'oob_score', 'warm_start']
    self.svm_conf = ['C', 'kernel', 'degree', 'gamma', 'coef0', 'shrinking', 'tol',
      'cache_size', 'svm_class_weight', 'max_iter', 'decision_function_shape', 'svm_random_state']
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
              $('#rf_conf').hide();
              $('#svm_conf').hide();
            }
            else if ($('#id_Classifier').val() === "rf")
            {
              $('#rf_conf').show();
              $('#cnn_conf').hide();
              $('#svm_conf').hide();
            }
            else if ($('#id_Classifier').val() === "svm")
            {
              $('#svm_conf').show();
              $('#cnn_conf').hide();
              $('#rf_conf').hide();
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
      Fieldset("Configurations for random forest classifier",
          MultiWidgetField(*self.rf_conf, attrs=({'style': 'width: 30%; display: inline-block;'})),
          id = 'rf_conf'
      ),
      Fieldset("Configurations for SVM classifier",
          MultiWidgetField(*self.svm_conf, attrs=({'style': 'width: 30%; display: inline-block;'})),
          id = 'svm_conf'
      ),
      HTML("""<script>$('#rf_conf').hide(); $('#svm_conf').hide();</script>"""),
      HTML("""</div></div>"""),
    )
    self.helper.add_input(Submit('create_classification_model_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))
  

  def create_classification_model(self, classifier_name, classifier_description, user, task_upload_file, task, vectorizer, classifier, conf_dict):

    model_path = get_path(str(user), classifier_name)
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
    else:
      path = "eval_" + str(task.title) + "_" + str(task.pk) + '.csv'
      with open(os.path.join(settings.MEDIA_ROOT, path), 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(reader)
        posts = []
        labels = []
        for r in reader:
          posts.append(r[0])
          labels.append(r[-1])

    conf_dict["vectorizer"] = vectorizer
    conf_dict["classifier"] = classifier
    conf_dict["data"] = posts
    conf_dict["labels"] = labels
    conf_dict["path"] = model_path
    verbose_name = str(user.id) + '|' + classifier_name
    query_api(url=self.train_url, payload=conf_dict, headers=self.headers, verbose_name=verbose_name)

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
    return None

class ClassifyDataForm(forms.Form):

  def __init__(self, *args, **kwargs):
    super(ClassifyDataForm, self).__init__(*args, **kwargs)
    self.classify_url = "http://localhost:6666/classify"
    self.headers = {'content-type': 'application/json'}
    self.fields['Classifier'] = forms.ModelChoiceField(queryset=Classify.objects.all(), required=True)
    self.fields['Upload Posts'] = forms.FileField(required=True)
    self.helper = FormHelper()
    self.helper.form_id = 'classify_data_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/classify/classify_data/'
    self.helper.layout = Layout(
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 1: Choose Your Classifier
          </div>
          <div class="panel-body">
          """),
      Field('Classifier', placeholder="Enter the classification task name..."),
      HTML("""</div></div>"""),
      HTML("""<div class="panel panel-info">
                                        <div class="panel-heading">
                                                Step 2: Source of Classify Data
                                        </div>
                                        <div class="panel-body"> """),
    
      Field('Upload Posts', placeholder = ""),
      HTML("""</div></div>"""),
    )
    self.helper.add_input(Submit('classify_data_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))

  def classify_data(self, classifier, task_upload_file, user):
    model_path = get_path(str(user), classifier.name)
    if not os.path.exists(model_path):
      return {'error': 'model not found'}
    if task_upload_file:
      reader = csv.reader(TextIOWrapper(task_upload_file), skipinitialspace=True)
      next(reader)
      posts = []
      labels = []
      for line in reader:
        posts.append(line[0])
        if len(line) > 1:
          labels.append(line[1])
    else:
      return {'error': 'file not valid'}
    if len(posts) < 1:
      return {'error': 'no test data'}
    if len(labels) > 0 and len(labels) != len(posts):
      return {'error': "posts and labels don't match"}
    classify_payload = {}
    classify_payload["path"] = model_path
    classify_payload["data"] = posts
    if len(labels) > 0:
      classify_payload["labels"] = labels
    print(classify_payload)
    response = requests.post(self.classify_url, data=json.dumps(classify_payload), headers=self.headers)
    predictions = json.loads(response.text)
    predictions["data"] = posts
    predictions["raw_labels"] = labels
    predictions["labels"] = list(set(labels))
    if "predictions" in predictions:
      prediction_path = os.path.join(settings.MEDIA_ROOT, str(user) + '-' + classifier.name + '-prediction.csv')
      with open(prediction_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(['posts', 'prediction labels'])
        for post, label in zip(posts, predictions['predictions']):
          writer.writerow([post, label])
      predictions['path'] = '/media/' + prediction_path.split('/')[-1]
    else:
      prediction_path = os.path.join(settings.MEDIA_ROOT, str(user) + '-' + classifier.name + '-confmatrix.csv')
      with open(prediction_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow([""] + predictions["labels"])
        for label in predictions["labels"]:
          row = [label]
          for i in range(len(predictions["labels"])):
            row.append(predictions['confusion_matrix'][label][predictions["labels"][i]])
          writer.writerow(row)
      predictions['path'] = '/media/' + prediction_path.split('/')[-1]

    return predictions