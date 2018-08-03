from django import forms
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Fieldset, ButtonHolder, HTML, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from quiz.models import Quiz, AnswerKey, Answer
from label.models import Label
from post.models import Post
import csv
from io import TextIOWrapper

'''main form to create the quiz'''
class CreateQuizForm(forms.Form):

  def __init__(self, *args, **kwargs):
    super(CreateQuizForm, self).__init__(*args, **kwargs)   

    self.fields['Quiz Title'] = forms.CharField(max_length=50, required=False)
    self.fields['Quiz Description'] = forms.CharField(widget=forms.Textarea, required=False)
    self.fields['Number of Questions'] = forms.IntegerField(required=False)
    self.fields['Pass Mark'] = forms.IntegerField(max_value=100, required=False)
    self.fields['Upload Quiz Posts and Labels'] = forms.FileField()
    self.helper = FormHelper()
    self.helper.form_id = 'create_quiz_form'
    self.helper.form_method = 'POST'
    self.helper.form_action = '/quiz/create_quiz/'
    self.helper.layout = Layout(
      HTML("""
          <div class="panel panel-info">
          <div class="panel-heading">
            Create Quiz
          </div>
          <div class="panel-body">
          """),
      Field('Quiz Title', placeholder="Enter the quiz title..."),
      Field('Quiz Description', placeholder="Write some description about the quiz..."),
      Field('Number of Questions', placeholder="Minimum number of questions to be responded by labelers for this quiz"),
      Field('Pass Mark', placeholder="Minimum score to be passed for this quiz"),
      Field('Upload Quiz Posts and Labels'),
      HTML("""
          <style> p.solid {border : 1px; display: inline-block ; border-style: solid;} </style>
          <!--table style="border: 1px solid black;"-->
          <tr>
          <td>
          <p class="solid">
          <b>Note</b> : Upload a csv file with <a href="/media/sample_quiz.csv" download="sample_quiz.csv">this sample format</a> <br/>[All labels separated with pipelines on the first line.<br/> Each post and its corresponding label on a separate line after that.]
          </td>
          </tr>
          </p>
          <!--/table-->
          """),
      HTML("""
          </div>
          </div>
          """),
      )
    self.helper.add_input(Submit('create_quiz_submit', 'Save', css_class='btn btn-info btn-sm pull-right'))

  '''create quiz model from the form data'''
  def create_quiz(self, quiz_title, quiz_description, max_posts, pass_mark, quiz_upload_file, user):
    try:
      quiz_object = Quiz.objects.create(
        title=quiz_title,
        description=quiz_description,
        max_posts=max_posts,
        pass_mark=pass_mark,
        creator=user, )
      readerR = csv.reader(TextIOWrapper(quiz_upload_file), delimiter='|', skipinitialspace=True)
      answer_key_object = AnswerKey.objects.create(quiz=quiz_object)
      label_list = []
      labels = next(readerR)
      for label in labels:
        label_object = Label.objects.create(content=label)
        label_list.append(label_object)
        quiz_object.label_list.add(label_object)
      posts = readerR
      for post in posts:
        post_object = Post.objects.create(
          content=post[0],
          author=user)
        quiz_object.post_list.add(post_object)
        answer_object = Answer.objects.create(
          answer_key=answer_key_object,
          post=post_object,
          label=[item for item in label_list if item.content == post[1]][0])
    except:
      return None
    return quiz_object


  def add_participant(self, task, coder):
    Participation.objects.create(task=task, coder=coder)

  def save_quiz(self, task):
    send_mail(subject, message, 'ucipt.labeling@gmail.com', coder_list, fail_silently=False)
    self.add_participant(task, coder)

