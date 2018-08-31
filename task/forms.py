from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.urlresolvers import resolve
import requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import MultiWidgetField, Row, Layout, Field, Submit, Fieldset, ButtonHolder, HTML, Button, Div
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from django.forms.fields import ChoiceField
from itertools import chain
from django.conf import settings
from django.http import JsonResponse
import random
import math
import string
import hashlib
import pymysql
from .models import Task, Participation, Connection, Colname, Tablename
from quiz.models import Quiz, AnswerKey, Answer
from label.models import Label
from post.models import Post
from smart_selects.form_fields import ChainedModelChoiceField
from django_select2.forms import ModelSelect2Widget
import os
import codecs
import csv
import unicodecsv
from io import TextIOWrapper
from django.core.exceptions import ValidationError
from response.models import PostResponse
from django.shortcuts import get_object_or_404
from django.forms import widgets
from django.template import loader
from functools import wraps
import errno
import os
import signal
import ipaddress
class TimeoutError(Exception):
  pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
  def decorator(func):
    def _handle_timeout(signum, frame):
      raise TimeoutError(error_message)
    def wrapper(*args, **kwargs):
      signal.signal(signal.SIGALRM, _handle_timeout)
      signal.alarm(seconds)
      try:
        result = func(*args, **kwargs)
      finally:
        signal.alarm(0)
      return result
    return wraps(func)(wrapper)
  return decorator

CHOICES = (('T', 'True',), ('F', 'False',))
QCHOICES = (('create', 'Create New Quiz',), ('choose', 'Choose From Available Quizes',))

'''check the size of the file'''
def file_size(value):
  limit = 20 * 1024 * 1024
  if value.size > limit:
    raise ValidationError('File too large. Size should not exceed 20 MiB.')
  if not value.name.endswith('.csv'):
    raise ValidationError('Please upload a csv file.')

'''main form to load the database'''
class LoadDatabaseForm(forms.Form):
  
  def __init__(self, *args, **kwargs):
    super(LoadDatabaseForm, self).__init__(*args, **kwargs)
    self.fields['Mysql Username'] = forms.CharField(max_length=255, required=False)
    self.fields['Mysql Host Address'] = forms.CharField(max_length=255, required=False)
    self.fields['Mysql Password'] = forms.CharField(max_length=255, required=False)
    self.fields['Mysql Database Name'] = forms.CharField(max_length=255, required=False)
    self.fields['Mysql Port Number'] = forms.IntegerField(initial=3306, required=False)
    self.fields['AsterixDB Host Address'] = forms.CharField(max_length=255, required=False)
    self.fields['AsterixDB Database Name'] = forms.CharField(max_length=255, required=False)
    self.fields['AsterixDB Port Number'] = forms.IntegerField(initial=19002, required=False)
    self.helper = FormHelper()
    self.helper.form_id = 'load_database_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/task/load_database/'
    self.helper.layout = Layout(
      HTML("""
          <script>$(function()
          {
              $('input[name=post-format-load]').on('click init-post-format', function() {
                  $('#gallery-box3').toggle($('#post-format-gallery-load').prop('checked'));
              }).trigger('init-post-format');
                   $('input[name=post-format-load]').on('click init-post-format', function() {
                  $('#gallery-box4').toggle($('#post-format-gallery-load1').prop('checked'));
              }).trigger('init-post-format');

          });
          </script>
          """),
      HTML("""
          <label><input type="radio" name="post-format-load" id="post-format-gallery-load">Load from Mysql</label><div></div>
          <div id="gallery-box3">
          """),
      Field('Mysql Username', placeholder="Enter the username"),
      Field('Mysql Host Address', placeholder="Enter the ip address of the host"),
      Field('Mysql Password', placeholder="Enter the password"),
      Field('Mysql Database Name', placeholder="Enter the name of the database"),
      Field('Mysql Port Number', placeholder="Enter the port of the database, default: 3306"),
      HTML("""</div><div>"""),
      HTML("""<label><input type="radio" name="post-format-load" id="post-format-gallery-load1">Load from AsterixDB</label>
          </div><div id="gallery-box4">
          """),
      Field('AsterixDB Host Address', placeholder="Enter the ip address of the host"),
      Field('AsterixDB Database Name', placeholder="Enter the name of the database"),
      Field('AsterixDB Port Number', placeholder="Enter the port of the database, default: 19002"),
      HTML("""</div><div>"""),
      HTML("""<button type="button" onclick="window.open('', '_self', ''); window.close();">Close</button>"""))
    # self.helper.add_input(Submit('load_database_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))

  def clean(self):
    cleaned_data = super(LoadDatabaseForm, self).clean()
    if not ((cleaned_data.get('Mysql Username') and cleaned_data.get('Mysql Host Address') and cleaned_data.get('Mysql Password') and cleaned_data.get('Mysql Database Name') and cleaned_data.get('Mysql Port Number')) or (cleaned_data.get('AsterixDB Host Address') and cleaned_data.get('AsterixDB Database Name') and cleaned_data.get('AsterixDB Port Number'))):
      raise forms.ValidationError('Must either load form Mysql or AsterixDB')
    return cleaned_data

  def load_database(self, c_username, c_ip, c_password, c_dbname, c_port, user):
    connection = None
    try:
      connection = pymysql.connect(host=c_ip,
                                   port=c_port,
                                   user=c_username,
                                   password=c_password,
                                   db=c_dbname,
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.Cursor)
    except Exception as e:
      code, error = e.args
      return {'error': error, 'code': code}, None
    db_obj = Connection.objects.create(
                                      creator=user,
                                      port=c_port,
                                      username=c_username,
                                      ip=c_ip,
                                      password=c_password,
                                      dbname=c_dbname,
                                      is_mysql=True
                                      )
    try:
      with connection.cursor() as cursor:
        cursor.execute("USE " + c_dbname)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        for table_name in table_names:
          table_obj = Tablename.objects.create(creator=user, tablename=table_name, connection=db_obj)   
          cursor.execute("SHOW columns FROM " + table_name)
          cols = cursor.fetchall()
          col_names = [col[0] for col in cols]
          table_obj.save()
          for col_name in col_names:
            col_obj = Colname.objects.create(creator=user, colname=col_name, tablename=table_obj)
            col_obj.save()
    except Exception as e:
      code, error = e.args
      return {'error': error, 'code': code}, None
    finally:
      connection.close()
    db_obj.save()
    return None, db_obj

  def load_database_A(self, c_ip, c_dbname, c_port, user):
    url = 'http://' + c_ip + ':' + str(c_port) + '/query/service'
    statement = 'use ' + c_dbname + ';'
    data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
    res = None
    try:
      res = requests.post(url, params=data_dict)
      if res.status_code != 200:
        res.raise_for_status()
    except Exception as e:
      if res and res.status_code != 200:
        return {'error': str(e), 'code': res.status_code}, None
      else:
        return {'error': str(e)}, None
    db_obj = Connection.objects.create(
                                      creator=user,
                                      port=c_port,
                                      ip=c_ip,
                                      dbname=c_dbname,
                                      is_mysql=False
                                      )
    try:
      statement = "SELECT VALUE ds FROM Metadata.`Dataset` ds WHERE ds.DataverseName='Default';"
      data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
      res = requests.post(url, params=data_dict)
      if res.status_code == 200:
        j_res = res.json()
        for entry in j_res['results']:
          table_name = entry['DatasetName']
          table_obj = Tablename.objects.create(creator=user, tablename=table_name, connection = db_obj)
          table_obj.save()
          statement = 'SELECT VALUE entry FROM ' + table_name + ' entry;'
          data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
          col_res = requests.post(url, params=data_dict)
          if res.status_code == 200:
            j_col_res = col_res.json()
            if len(j_col_res['results']) > 0:
              for col_name in j_col_res['results'][0].keys():
                col_obj = Colname.objects.create(creator=user, colname=col_name, tablename=table_obj)
                col_obj.save()
          else:
            col_res.raise_for_status()
      else:
        res.raise_for_status()
    except Exception as e:
      if res and res.status_code != 200:
        return {'error': str(e), 'code': res.status_code}, None
      elif col_res and col_res.status_code != 200:
        return {'error': str(e), 'code': col_res.status_code}, None
      else:
        return {'error': str(e)}, None
    db_obj.save()
    return None, db_obj

class LoadDatabaseModalForm(LoadDatabaseForm):
  def __init__(self, *args, **kwargs):
    super(LoadDatabaseModalForm, self).__init__(*args, **kwargs)
    self.helper.form_id = 'load_database_form_modal'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/task/load_database_modal/'
    self.helper.layout = Layout(
      HTML("""
          <script>
          function IsJsonString(str) {
              try {
                  JSON.parse(str);
              } catch (e) {
                  return false;
              }
              return true;
          }
          $('#load_database_form_modal').submit(function(e){
            $('.error').html('please wait...')
             $.ajax({
                  type: 'POST',
                  url: '/task/load_database_modal/',
                  data: $('#load_database_form_modal').serialize(),
                  success: function (data) {
                      var jstring = JSON.stringify(data, undefined, 1).replace(/[{}]/g, '');
                      if (jstring.includes('Must either load form Mysql or AsterixDB')){
                        $('.error').html('Must either load form Mysql or AsterixDB');
                      }
                      else{
                        $('.error').html(jstring);
                      }
                  },
                  error: function(data) {
                      $('.error').html('Must either load form Mysql or AsterixDB');
                  }
              });
              e.preventDefault();
          });
          $(function()
              {
              $('input[name=post-format-load]').on('click init-post-format', function() {
                  $('#gallery-box3').toggle($('#post-format-gallery-load').prop('checked'));
              }).trigger('init-post-format');
                   $('input[name=post-format-load]').on('click init-post-format', function() {
                  $('#gallery-box4').toggle($('#post-format-gallery-load1').prop('checked'));
              }).trigger('init-post-format');
              });

          </script>
          """),
      HTML("""
          <label><input type="radio" name="post-format-load" id="post-format-gallery-load">Load from Mysql</label><div></div>
          <div id="gallery-box3">
          """),
      Field('Mysql Username', placeholder="Enter the username"),
      Field('Mysql Host Address', placeholder="Enter the ip address of the host"),
      Field('Mysql Password', placeholder="Enter the password"),
      Field('Mysql Database Name', placeholder="Enter the name of the database"),
      Field('Mysql Port Number', placeholder="Enter the port of the database, default: 3306"),
      HTML("""</div><div>"""),
      HTML("""<label><input type="radio" name="post-format-load" id="post-format-gallery-load1">Load from AsterixDB</label>
          </div><div id="gallery-box4">
          """),
      Field('AsterixDB Host Address', placeholder="Enter the ip address of the host"),
      Field('AsterixDB Database Name', placeholder="Enter the name of the database"),
      Field('AsterixDB Port Number', placeholder="Enter the port of the database, default: 19002"),
      HTML("""</div><div>"""),
      )

'''main form to create the task'''
class CreateTaskForm(forms.Form):
  connection = forms.ModelChoiceField(queryset=Connection.objects.all(), label=u'Select Database to Load', required=False, widget=ModelSelect2Widget(model=Connection, search_fields=['username__icontains'], attrs={'data-placeholder': 'select database','data-width': '50em'  })) 
  tablename_post = forms.ModelChoiceField(queryset=Tablename.objects.all(), label=u'Select Post Table(max 10000)', required=False, widget=ModelSelect2Widget(model=Tablename, search_fields=['tablename__icontains'], dependent_fields={'connection': 'connection'}, max_results=20, attrs={'data-placeholder': 'select post table', 'data-width': '50em'}))
  colname_post = forms.ModelChoiceField(queryset=Colname.objects.all(), label=u'Select Post Column', required=False, widget=ModelSelect2Widget(model=Colname, search_fields=['colname__icontains'], dependent_fields={'tablename_post': 'tablename'}, max_results=20, attrs={'data-placeholder': 'select post column', 'data-width': '50em'}))
  upload = forms.FileField(label=u'Upload Task Posts and Labels(maximun 20 MiB)',required=False, validators=[file_size])
  label = forms.CharField(max_length=255, label=False, required=False)
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user')
    super(CreateTaskForm, self).__init__(*args, **kwargs)
    self.fields['Task Title'] = forms.CharField(max_length=50)
    self.fields['Task Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Min number of posts that a labeler should complete'] = forms.IntegerField(initial=5, required=False, help_text='Once a labeler labels this number of posts, his/her task willbe marked as complete. However, he/she can keep labeling more posts.')
    self.fields['Min number of labelers per post'] = forms.IntegerField(initial=1, required=False, help_text='Each post will be assigned to this number of labelers, before more posts are assigned. Use a larger number if the task is harder or the reliability of the labelers is lower.')
    self.fields['Choose Quiz'] =forms.ModelChoiceField(queryset=Quiz.objects.all(), required=False)
    self.fields['Quiz Title'] = forms.CharField(max_length=50, required=False)
    self.fields['Quiz Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Number of Questions'] = forms.IntegerField(required=False)
    self.fields['Pass Mark'] = forms.IntegerField(max_value=100, required=False)
    self.fields['Label Posts in Random Order'] =  forms.CharField(max_length=5, widget=forms.Select(choices=CHOICES))
    self.fields['Participating Labelers'] = forms.CharField(widget=forms.Textarea, required=False)
    self.helper = FormHelper()
    self.helper.form_id = 'create_task_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/task/create_task/'
    self.helper.layout = Layout(
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 1: Create Task
          </div>
          <div class="panel-body">
          """),
      Field('Task Title', placeholder="Enter the task title..."),
      Field('Task Description', placeholder="Write some description about the task..."),
      Field('Min number of posts that a labeler should complete', placeholder="Minimum number of posts to be labeled by labelers for this task"),
      Field('Min number of labelers per post', placeholder="Minimum number of labelers per post"),      
      HTML(""""""),
      Field('Label Posts in Random Order', placeholder=""),
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
          <label><input type="radio" name="post-format" id="post-format-gallery">Load from CSV</label><div></div>
          <div id="gallery-box">
          """),
      Field('upload', placeholder = ""),
      HTML("""<script>
          function buildHtmlTable(selector) {
            var columns = addAllColumnHeaders(myList, selector);

            for (var i = 0; i < myList.length; i++) {
              var row$ = $('<tr/>');
              for (var colIndex = 0; colIndex < columns.length; colIndex++) {
                var cellValue = myList[i][columns[colIndex]];
                if (cellValue == null) cellValue = "";
                row$.append($('<td/>').html(cellValue));
              }
              $(selector).append(row$);
            }
          }

          function addAllColumnHeaders(myList, selector) {
            var columnSet = [];
            var headerTr$ = $('<tr/>');

            for (var i = 0; i < myList.length; i++) {
              var rowHash = myList[i];
              for (var key in rowHash) {
                if ($.inArray(key, columnSet) == -1) {
                  columnSet.push(key);
                  headerTr$.append($('<th/>').html(key));
                }
              }
            }
            $(selector).append(headerTr$);

            return columnSet;
          }

          function custom_alert( message, title ) {
              if ( !title )
                  title = 'Table View';

              if ( !message )
                  message = 'No Message to Display.';
              var html;
              if (typeof message == 'string') html = message
              else {
            $.each(message, function (index, item) {
                  if (index === 0) {
                      html += "<tr>";
                      $.each(item, function (vlaIndex) {
                          html += "<td>";
                          html += vlaIndex;
                          html += "</td>";
                      });
                      html += "</tr>";
                  }
                  html += "<tr>";
                  $.each(item, function (vlaIndex, valItem) {
                      html += "<td>";
                      html += valItem;
                      html += "</td>";
                  });
                  html += "</tr>";
              });
            }
              $('<div></div>').html(html).dialog({
                  title: title,
                  resizable: false,
                  modal: true,
                  buttons: {
                      'Ok': function()  {
                          $( this ).dialog( 'close' );
                      }
                  }
              });
          }

          function getCookie(name) {
              var cookieValue = null;
              if (document.cookie && document.cookie != '') {
                  var cookies = document.cookie.split(';');
                  for (var i = 0; i < cookies.length; i++) {
                      var cookie = jQuery.trim(cookies[i]);
                      // Does this cookie string begin with the name we want?
                      if (cookie.substring(0, name.length + 1) == (name + '=')) {
                          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                          break;
                      }
                  }
              }
              return cookieValue;
          }

          var csrftoken = getCookie('csrftoken');

          function csrfSafeMethod(method) {
              // these HTTP methods do not require CSRF protection
              return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
          }

          $.ajaxSetup({
              beforeSend: function(xhr, settings) {
                  if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                      xhr.setRequestHeader("X-CSRFToken", csrftoken);
                  }
              }
          });

          var fileInput = document.getElementById('id_upload');

          fileInput.addEventListener('input', function(e) {
              var file = fileInput.files[0];
              var textType = /text.*/;
              if (file.type.match('text.*|image.*|application.*')) {
                  var reader = new FileReader();
                  reader.onload = function(e) {
                      var content = reader.result;
                display = content.replace(/(\\n+)/g, '<br>');
                      custom_alert(display.split('<br>').slice(0,10).join('<br></br>'));
                  }
                  reader.readAsText(file);
              } else {
                  alert("File not supported!");
              }
          });

          $(document).ready(function(){
            $("#myModal").on("show.bs.modal", function(e) {
              var link = $(e.relatedTarget);
              $(this).find(".modal-body").load(link.attr("href")).end();
          });

          var tables = $("#id_tablename_post");
          tables.attr("disabled", true);
          var cols = $("#id_colname_post");
          cols.attr("disabled", true);

          $("#id_connection").change(function()
          {
            console.log($('#id_connection').val())
            if ($('#id_connection').val() === "")
            {
              tables.attr("disabled", true);
              cols.attr("disabled", true);
            }
            else
            {
              tables.attr("disabled", false);
            }
          });
          $("#id_tablename_post").change(function() {
            console.log($('#id_tablename_post').val())
            if ($('#id_tablename_post').val() === "")
            {cols.attr("disabled", true);}
            else
            {cols.attr("disabled", false);}
            $.post('get_table/',
              {
                'table_id': $('#id_tablename_post').val()
              },
                function(data){
                  if (typeof data[0][Object.keys(data[0])[0]] == 'object') custom_alert(JSON.stringify(data.slice(0,10), null, 2));
                  else custom_alert(data.slice(0,10));
                });
              });
            });
            function change_modal_connection() {
              eModal.ajax("/task/connection_list_modal", 'Connection List');
              eModal.setId('main_list');
            }
            </script>
            """),
      HTML("""<style> p.solid {border : 1px; display: inline-block ; border-style: solid;} </style>
          <tr>
          <td>
          <p class="solid">
          <b>Note</b> : Upload a csv file with <a href="/media/sample_survey1.csv" download="sample_survey1.csv">this sample format</a> <br/>[All labels separated with pipelines on the first line. <br/>Each post on a separate line after that.]
          </td>
          </tr>
          </p>
          <!--/table-->
          """),

      HTML("""</div><div>"""),
      HTML("""
          <label><input type="radio" name="post-format" id="post-format-gallery1">Load from database</label>
          </div><div id="gallery-box1">
          """),
      HTML("""<script> function popupfunc() {window.open("http://dblab-rack30.cs.ucr.edu/task/load_database","popup_page","status=1,height:500,width:600,toolbar=0,resizeable=0") } </script>"""),
      HTML("""<script> function popupfunc_a() {window.open("http://dblab-rack30.cs.ucr.edu/task/connection_list","popup_page","status=1,height:500,width:600,toolbar=0,resizeable=0") } </script>"""),
      HTML("""<p style="color:blue">i.Connect to Database:</p>"""),
      HTML("""<p>You may connect to database <a href='#' onclick="popupfunc()">here</a> if you haven't created one.</p>"""),
      HTML("""<p>Or manage your database instances <a href='#' onclick="popupfunc_a()">here(popup)</a> or <a href="javascript:void(0);" onclick="change_modal_connection();">here(modal).</a></p></p>"""),

      HTML("""<p style="color:blue">ii.Select Your Posts:</p>"""),
      Field('connection', css_class='col-md-4'),
      Field('tablename_post', css_class='col-md-4'),
      Field('colname_post', css_class='col-md-4'),
      HTML("""<p style="color:blue">iii.Type in Your Labels </p>"""),
      Field('label', placeholder=" label1;label2;label3..."),
      HTML("""</div></div><div>"""),
      HTML("""
          <div class="panel panel-info">
          <div class="panel-heading">
            Step 2: Choose/Create Quizzes (Optional)
            <!--span title="You can either create a new quiz or choose one from the provided list">?</span-->   
          <!--img src="help.png" alt="Nature" onmouseover="helpText()" onmouseout="helpBack()"-->
          </div>
          <div class="panel-body">
          <p> <b>Note</b>: This is an optional prerequisite quiz for the task. You may select quizzes from the given list or create a new one <a href="http://dblab-rack30.cs.ucr.edu/quiz/create_quiz/">here</a>.</p>
          """),

      Field('Choose Quiz', placeholder=""),
      HTML("""</div></div>"""),
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 3: Send Task
          </div>
          <div class="panel-body">
          <p> <b>Note</b>: Enter the labelers to participate in the task line by line </p>
          """),
      Field('Participating Labelers', placeholder=" labeler1@example.com \n labeler2@example.com \n ..."),
      HTML("""</div></div>"""),
      )
    self.helper.add_input(Submit('create_task_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))
    self.helper.add_input(Submit('Preview', 'Preview', css_class='btn btn-info btn-sm pull-left'))

  def clean(self):
    cleaned_data = super(CreateTaskForm, self).clean()
    if not (cleaned_data.get('upload') or (cleaned_data.get('connection') and cleaned_data.get('tablename_post') and cleaned_data.get('colname_post') and cleaned_data.get('label'))):
      raise forms.ValidationError('Must either load form CSV or database')
    if cleaned_data.get('upload'):
      lines = cleaned_data.get('upload').readlines()
      count = len(lines) - 1
      for line in lines[1:]:
        if len(line) > 1000:
          raise forms.ValidationError('Post too long: ' + str(line))
      len_coder = len(cleaned_data.get('Participating Labelers').split('\n'))
      min_pl = cleaned_data.get('Min number of posts that a labeler should complete')
      min_lp = cleaned_data.get('Min number of labelers per post')
      cleaned_data['count'] = count
      cleaned_data['min_lp'] = min_lp
      cleaned_data['min_pl'] = min_pl
      cleaned_data['len_coder'] = len_coder
      cleaned_data.get('upload').seek(0)
      if count < cleaned_data.get('Min number of posts that a labeler should complete'):
        raise forms.ValidationError('Number of posts not enough!')
    if len(cleaned_data.get('Participating Labelers').split('\n')) < cleaned_data.get('Min number of labelers per post'):
      raise forms.ValidationError('Participating Labelers not enough!')

    if Task.objects.filter(title=cleaned_data['Task Title'], creator=self.user.pk).count() > 0:
      raise forms.ValidationError("Existing title found, please use a different task name.")
    return cleaned_data

  def create_task(self, task_title, task_description, user, prerequisite, task_num_labelers, task_num_posts, task_random_label, task_upload_file, db_info, post_name,post_col_name, labels):
    has_id = False
    try:
      if task_upload_file is not None:
        readerR = csv.reader(TextIOWrapper(task_upload_file, errors='ignore'), delimiter='|', skipinitialspace=True)
        labelsF = next(readerR)
        posts = readerR
      elif db_info is not None and post_name is not None and post_col_name is not None and labels is not None:
        if db_info.is_mysql:
          conn = pymysql.connect(host=db_info.ip,
                                port=db_info.port,
                                user=db_info.username,
                                password=db_info.password,
                                db=db_info.dbname,
                                cursorclass=pymysql.cursors.Cursor
                                )
          post_dict = {}
          try:
            cur = conn.cursor()
            cur.execute("SELECT " + post_col_name.colname + " FROM " + post_name.tablename + " LIMIT 10000")
            posts = list(cur.fetchall())
            labelsF = labels.strip().split(';')
            print(labelsF)
            cur.execute("SELECT id FROM " + post_name.tablename + " LIMIT 10000")
            ids = list(cur.fetchall())
            has_id = True
          finally:
            cur.close()
            conn.close()
        else:
          url = 'http://' + db_info.ip + ':' + str(db_info.port) + '/query/service'
          statement = 'use ' + db_info.dbname + ';'
          data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
          try:
            res = requests.post(url, params=data_dict)
            if res.status_code != 200:
              return None
          except:
            return None
          statement = 'SELECT VALUE entry.' + post_col_name.colname + ' FROM ' + post_name.tablename+' entry LIMIT 10000;'
          data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
          res = requests.post(url, params=data_dict)
          if res.status_code == 200:
            j_res = res.json()
            posts = [(i,) for i in j_res['results']]
          labelsF = labels.strip().split(';')
          statement = 'SELECT VALUE entry.id FROM ' + post_name.tablename + ' entry LIMIT 10000;'
          data_dict = {'statement': statement, 'pretty': 'true', 'client_context_id': 'secret'}
          res = requests.post(url, params=data_dict)
          if res.status_code == 200:
            j_res = res.json()
            if j_res['results'] != [None] * len(j_res['results']):
              has_id = True
              ids = [(i,) for i in j_res['results']]
      else:
        return None
      if has_id:
        post_dict = dict(zip([i[0] for i in posts], [i[0] for i in ids]))
      task_obj = Task.objects.create(
                                    title=task_title,
                                    description=task_description,
                                    num_posts=task_num_posts,
                                    num_labelers=task_num_labelers,
                                    random_label=task_random_label,
                                    connection=db_info,
                                    table_name=post_name,
                                    creator=user,
                                    prerequisite=prerequisite,
                                    upload_task=task_upload_file
                                    )
      self.id = task_obj.id
      list2_shuf_temp = []
      ctr = 0
      for post in posts:
        if post != []:
          list2_shuf_temp.append(post[0])
          ctr = ctr + 1
      if task_random_label == 'T':
        list1_shuf = []
        list2_shuf = []
        index_shuf = range(ctr)
        index_shuf1 = [i for i in range(ctr)]
        random.shuffle(index_shuf1)
        for i in index_shuf1:
            temp = list2_shuf_temp[i]
            list2_shuf.append(temp)
        list1_shuf = labelsF
      else:
          list2_shuf = list2_shuf_temp
          list1_shuf = labelsF

      for label in list1_shuf:
        label_object = Label.objects.create(content=label)
        task_obj.label_list.add(label_object)
      for post in list2_shuf:
        if has_id:
          post_object = Post.objects.create(
                                         content=post,
                                         author=user,
                                         db_id=int(post_dict.get(post)),
                                         )
        else:
          post_object = Post.objects.create(
                                         content=post,
                                         author=user,
                                         )
        task_obj.post_list.add(post_object)
        task_obj.save()
    except:
      return None

    return task_obj

  def create_quiz(self, quiz_title, quiz_description, max_posts, pass_mark, quiz_upload_file, user):
    try:
      csvfile = open(str(quiz_upload_file), 'rb')
      readerR = csv.reader(csvfile, delimiter='|', skipinitialspace=True)
      quiz_object = Quiz.objects.create(
                                       title=quiz_title,
                                       description=quiz_description,
                                       max_posts=max_posts,
                                       pass_mark=pass_mark,
                                       creator=user)

      answer_key_object = AnswerKey.objects.create(quiz=quiz_object)
      label_list = []
      labelsF = next(readerR)
      for label in labelsF:
        label_object = Label.objects.create(content=label)
        label_list.append(label_object)
        quiz_object.label_list.add(label_object)
      postsF = readerR
      for post in postsF:
        post_object = Post.objects.create(
                                         content=post[0],
                                         author=user
                                         )
        quiz_object.post_list.add(post_object)
        answer_object = Answer.objects.create(
                                             answer_key=answer_key_object,
                                             post=post_object,
                                             label=[item for item in label_list if item.content == post[1]][0]
                                             )
    except:
      return None
    return quiz_object


  def add_participant(self, task, coder):
    Participation.objects.create(
                                task=task,
                                labeler=coder,
                                )

  def send_email(self, task):
    participating_coders = self.cleaned_data['Participating Labelers']
    coder_list = participating_coders.split()
    print (coder_list)
    coder_l = []
    for index, coderP in enumerate(coder_list):
      self.add_participant(task, coderP)
      coder_l.append(coderP)
      coder_l = []
      passwrd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
      passw = hashlib.sha224(passwrd.encode('utf-8')).hexdigest()
      User = get_user_model()
      if not User.objects.filter(email=coderP):
        User.objects.create(email=coderP)
        user = User._default_manager.get(email=coderP)
        user.set_password(passwrd)
        user.save()
        subject = str.format("Task created for {0}", coderP)
        message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.eduaccount/login\n Your password :{1} \nBest,\nSocial Post Analyzer System", coderP, passwrd)
        coder_l.append(coderP)
        send_mail(subject, message, settings.EMAIL_FROM, coder_l, fail_silently=False)
      else:
        user = User._default_manager.get(email=coderP)
        subject = str.format("Task created for {0}", coderP)
        message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n\nBest,\nSocial Post Analyzer System", coderP)
        coder_l.append(coderP)
        send_mail(subject, message, settings.EMAIL_FROM, coder_l, fail_silently=False)

'''main form to edit the task'''
class EditTaskForm(forms.Form):
  model = Task
  def __init__(self, *args, **kwargs):
    super(EditTaskForm, self).__init__(*args, **kwargs)
    self.fields['Task Title'] = forms.CharField(max_length=50)
    self.fields['Task Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Min Number of Posts'] = forms.IntegerField(required=False)
    self.fields['Min Number of Labelers'] = forms.IntegerField(required=False)
    self.fields['Upload Task Posts and Labels'] = forms.FileField()
    self.fields['Choose Quiz'] =forms.ModelChoiceField(queryset=Quiz.objects.all(), required=False)##forms.CharField(max_length=5, widget=forms.Select(choices=QCHOICES))
    self.fields['Quiz Title'] = forms.CharField(max_length=50, required=False)
    self.fields['Quiz Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Number of Questions'] = forms.IntegerField(required=False)
    self.fields['Pass Mark'] = forms.IntegerField(max_value=100, required=False)
    self.fields['Label Posts in Random Order'] =  forms.CharField(max_length=5, widget=forms.Select(choices=CHOICES))
    self.fields['Upload Quiz Posts and Labels'] = forms.FileField(required=False)
    self.fields['Participating Labelers'] = forms.CharField(widget=forms.Textarea, required=False)
    title = Task.objects.filter(title=self.Task.title)
    print (title)
    self.helper = FormHelper()
    self.helper.form_id = 'edit_task_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/task/edit_task/'
    self.helper.layout = Layout(
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 1: Create Task
          </div>
          <div class="panel-body">
          """),
      Field('Task Title', placeholder=""),
      Field('Task Description', placeholder="Write some description about the task..."),
      Field('Min Number of Posts', placeholder=""),
      Field('Min Number of Labelers', placeholder=""),
      Field('Label Posts in Random Order', placeholder=""),
      Field('Upload Task Posts and Labels', placeholder ="Upload us one post per line"),
      HTML("""</div>
          </div>"""),
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 2: Choose/Create Quiz (Optional)
            <script type="text/javascript">
            function helpText() {
                document.getElementById("help").innerHTML = " This is a help text";
            }

            function helpBack() {
                document.getElementById("help").innerHTML = "?";
            }
              </script>
          <div id="help" onmouseover="helpText()" onmouseout="helpBack()">?</div>
          </div>
          <div class="panel-body">
          <p> <b>Note</b>: This is an optional prerequisite quiz for the task. You may select quizzes from the given list or create a new one <a href="http://dblab-rack30.cs.ucr.edu/quiz/create_quiz/">here</a>.</p>
          """),
      Field('Choose Quiz', placeholder=""),
      HTML("""</div></div>"""),
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Step 3: Send Task
          </div>
          <div class="panel-body">
          <p> <b>Note</b>: Enter the coders to participate in the task line by line </p>
          """),
      Field('Participating Labelers', placeholder=" coder1@example.com \n coder2@example.com \n ..."),
      HTML("""</div></div>"""),
      )
    self.helper.add_input(Submit('edit_task_submit', 'Submit', css_class='btn btn-info btn-sm pull-right'))

  '''edit task based on the form data'''
  def edit_task(self, task_title, task_description, user, prerequisite, task_num_labelers, task_num_posts, task_random_label, task_upload_file):
      
    try:
      csvfile = open(str(task_upload_file), 'rb')
      readerR = csv.reader(csvfile, delimiter='|', skipinitialspace=True)
      labelsF = next(readerR)
      task_obj = Task.objects.create(
                                    title=task_title,
                                    description=task_description,
                                    num_labelers=task_num_labelers,
                                    num_posts=task_num_posts,
                                    random_label=task_random_label,
                                    prerequisite=prerequisite,
                                    creator=user
                                    )
      for label in labelsF:
        label_object = Label.objects.create(content=label)
        task_obj.label_list.add(label_object)
      posts = readerR
      for post in posts:
        post_object = Post.objects.create(
                                         content=post[0],
                                         author=user
                                         )
        task_obj.post_list.add(post_object)
    except:
      return None
    return task_obj


'''self created widget for deletion of labeler'''
class MyWidget(widgets.TextInput):
    template_name = 'task/custom_button.html'


'''main form the update the labeler'''
class UpdateLabelerForm(forms.Form):

  selectTask = forms.CharField(required=False)
  def __init__(self, *args, **kwargs):
    initial_arguments = kwargs.get('initial', None)
    print(initial_arguments)
    updated_initial = {}
    extra_fields = 0
    if initial_arguments:
      taskname = initial_arguments.get('Select Task', None)
      labelers = initial_arguments.get('Participating Labelers', None)
      task_id = initial_arguments.get('Task Id', None)
      updated_initial['ID'] = task_id
      updated_initial['Select Task'] = taskname
      tl = labelers.replace('\n', '')
      tl = tl.replace('b\'', '\'')
      tl = tl.replace("\'", '')
      tl = tl.replace(',', '\n')
      tl = tl.replace("[", "")
      tl = tl.replace("]", "")
      tl = tl.replace(" ", "")
      print (tl)
      updated_initial['Participating Labelers'] = tl
      tl_list = tl.split('\n')
      extra_fields = len(tl_list)
      if int(initial_arguments.get('extra', 0)) > extra_fields:
        extra_fields = initial_arguments.get('extra', 0)
      updated_initial['extra_field_count'] = extra_fields
      kwargs.update(initial=updated_initial)
    super(UpdateLabelerForm, self).__init__(*args, **kwargs)
    self.fields['extra_field_count'] = forms.IntegerField(required=False)
    self.fields['extra_field_count'].widget = forms.HiddenInput()
    self.fields['extra_field_count'].widget.attrs.update({'id': 'extra_field_count'})
    print(extra_fields)
    labeler_fields = []
    for index in range(int(extra_fields)):
      labeler_fields.append('labeler_{index}'.format(index=index))
      self.fields['labeler_{index}'.format(index=index)] = forms.CharField(required=False, widget=MyWidget)
      self.fields['labeler_{index}'.format(index=index)].widget.attrs.update({'name': index})
      self.fields['labeler_{index}'.format(index=index)].label = False
      if index < len(tl_list):
        self.fields['labeler_{index}'.format(index=index)].initial = tl_list[index]
        self.fields['labeler_{index}'.format(index=index)].widget.attrs.update({'id': 'labeler_{index}'.format(index=index)})
    self.fields['Select Task'] = forms.CharField(required=False)
    self.fields['Select Task'].widget.attrs['readonly'] = True
    self.fields['Detele responses when removing labelers'] = forms.BooleanField(initial = False, help_text='Caution: When chosen, if a user is removed, it will delete all his responses', required=False)
    self.fields['Detele responses when removing labelers'].widget.attrs.update({'id': 'delete_response'})
    self.fields['ID'] = forms.CharField(required=False)
    self.fields['ID'].widget = forms.HiddenInput()
    self.fields['Participating Labelers'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Participating Labelers'].widget = forms.HiddenInput()
    self.fields['Participating Labelers'].widget.attrs.update({'id': 'all_labelers'})
    
    self.helper = FormHelper()
    self.helper.form_id = 'update_labeler_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/task/update_labeler/'
    self.helper.layout = Layout(
      HTML("""<div class="panel panel-info">
          <div class="panel-heading">
            Add or Remove Labeler
          </div>"""),
      HTML("""<div class="panel-body"><p><b>Note</b>: Select a task and add/delete a labeler.</p>"""),
      Field('Select Task', placeholder=""),
      Field('Detele responses when removing labelers', placeholder=""),
      Field('ID', placeholder=""),
      Field('Participating Labelers', placeholder="coder1@example.com \n coder2@example.com \n ..."),
      Field('extra_field_count'),
      Fieldset("All Participating Labelers",
          MultiWidgetField(*labeler_fields, attrs=({'style': 'width: 30%; display: inline-block;'}, {'class': 'second_widget_class'})),
      ),
      HTML("""<button name = 'additem' class="btn btn-primary btn-md" onclick="add_field()">add another</button>"""),
      HTML("""<script>
          var inilabler = document.getElementById("all_labelers").value;
          
          function remove_field(id) {
              console.log(id);
              form_count = document.getElementById("extra_field_count").value;
              
              form_count--;
              if (document.getElementById(id))
              {
                (elem=document.getElementById(id)).parentNode.removeChild(elem);
              }
              $("[name=extra_field_count]").val(form_count);
          }
          function add_field() {
              form_count = document.getElementById("extra_field_count").value;
              console.log(form_count);
              form_count++;
              var element = $('<input type="text"/>');
              element.attr('name', 'labeler_' + form_count);
              $("#forms").append(element);
              $("[name=extra_field_count]").val(form_count);
          }
          function arr_diff (a1, a2) {
            var a = [], diff = [];
            for (var i = 0; i < a1.length; i++) {
              a[a1[i]] = true;
            }
            for (var i = 0; i < a2.length; i++) {
              if (a[a2[i]]) {
                delete a[a2[i]];
              } else {
              }
            }
            for (var k in a) {
              diff.push(k);
            }
            return diff;
          }
          
          function clicked(e)
          {
            var inilist = inilabler.split(/(\\n+)/g);
            var newlabler = document.getElementById("all_labelers").value;
            var newlist = newlabler.split(/(\\n+)/g);
            var delete_response = document.getElementById("delete_response").checked;
            var diff = arr_diff(inilist, newlist).join('\\n');
            if(diff != []) {
              if(!delete_response){
                if(!confirm('You will delete following labelers(without the responses):\\n' + diff +'\\nAre you sure you want to proceed?'))e.preventDefault();
              }
              else{
                if(!confirm('You will delete following labelers(with the responses):\\n' + diff +'\\nAre you sure you want to proceed?'))e.preventDefault();
              }
            }
          }
          </script>
          """),
      )
    self.helper.add_input(Submit('update_labeler_submit', 'Submit', onclick="clicked(event)", css_class='btn btn-info btn-sm pull-right'))

  '''update labeler based on the form data'''
  def update_labeler(self, task, participating_coders,tid,delete_response):
      
    try:
      coder_list = participating_coders.split()
      participation_obj = None
      o_coder_list = [i for i in Participation.objects.filter(task_id=tid).values_list('labeler', flat=True)]
      User = get_user_model()
      for coderP in o_coder_list:
        if coderP not in coder_list:
          userP = get_object_or_404(User, email=coderP)
          if delete_response:
            PostResponse.objects.filter(responder=userP.pk, task_id=tid).delete()
          Participation.objects.filter(labeler=coderP, task_id=tid).delete()
      for coderP in coder_list:
        coderP = coderP[0:]
        coder_l = []
        if not Participation.objects.filter(labeler=coderP, task_id=tid):
          participation_obj = Participation.objects.create(
                                                          task_id=tid,
                                                          labeler=coderP
                                                          )
          passwrd = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
          passw = hashlib.sha224(passwrd.encode('utf-8')).hexdigest()
          User = get_user_model()
          if not User.objects.filter(email=coderP) :
            User.objects.create(email=coderP)
            user = User._default_manager.get(email=coderP)
            user.set_password(passwrd)
            user.save()
            subject = str.format("Task created for {0}", coderP)
            message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n Your password :{1} \nBest,\nSocial Post Analyzer System", coderP, passwrd)
            coder_l.append(coderP)
            send_mail(subject, message, settings.EMAIL_FROM, coder_l, fail_silently=False)
          else:
            user = User._default_manager.get(email=coderP)
            subject = str.format("Task created for {0}", coderP)
            message = str.format("Hi {0},\n\n\tYou have been selected to complete a task. Please start here: http://dblab-rack30.cs.ucr.edu/account/login\n \nBest,\nSocial Post Analyzer System", coderP)
            coder_l.append(coderP)
            send_mail(subject, message, settings.EMAIL_FROM, coder_l, fail_silently=False)
    except:
      return None

    return participation_obj

  '''get the first element of an iterable object'''
  def get_first(iterable, default=None):
    if iterable:
      for item in iterable:
        print(item)
        return item
      print(iterable)
    return default

