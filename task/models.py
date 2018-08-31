from django.db import models  
from django.conf import settings
from django.forms.fields import ChoiceField
from django.urls import reverse
from label.models import Label1
from label.models import Label
from post.models import Post
from quiz.models import Quiz
#from participation.models import Participation

from django import forms 
from django.core.validators import MinValueValidator
from smart_selects.db_fields import ChainedForeignKey

CHOICES = (('T', 'True'),('F', 'False'),)

class Connection(models.Model):

  class Meta:
    verbose_name = 'db connection'
    verbose_name_plural = 'db connections'
    unique_together = ('username', 'ip', 'dbname', 'port')
  creator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    verbose_name = 'creator',
    blank = False,
    default = None,
    null = False,
    editable = False,)
  username = models.CharField(
    max_length = 255,
    verbose_name = 'username',
    default = 'AsterixDB',
    blank = False)
  ip = models.CharField(
    max_length = 255,
    verbose_name = 'ip',
    blank = False)
  password = models.CharField(
    max_length = 255,
    verbose_name = 'password',
    default = 'AsterixDB',
    blank = False)
  dbname = models.CharField(
    max_length = 255,
    verbose_name = 'dbname',
    blank = False)
  port = models.PositiveIntegerField(
    verbose_name = 'port',
    default = 3306,
    blank = False)
  is_mysql = models.BooleanField(
    verbose_name = 'is_mysql',
    default = True,
    blank = False)

  def __str__(self):
    return str(self.username)+'-'+str(self.dbname)+'-'+str(self.ip)

  def get_absolute_url(self):
    return reverse('task:connection_detail', kwargs={'pk': str(self.id)})



class Tablename(models.Model):

  class Meta:
    verbose_name = 'table names'
    verbose_name_plural = 'table names'
  creator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    verbose_name = 'creator',
    blank = False,
    default = None,
    null = False,
    editable = False,)
  tablename = models.CharField(
    max_length = 255,
    verbose_name = 'table name',
    blank = False)

  connection = models.ForeignKey(Connection,on_delete=models.CASCADE, related_name="tablenames")


  def __str__(self):
    return str(self.tablename)
  

class Colname(models.Model):

  class Meta:
    verbose_name = 'column names'
    verbose_name_plural = 'column names'
  creator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    verbose_name = 'creator',
    blank = False,
    default = None,
    null = False,
    editable = False,)
  colname = models.CharField(
    max_length = 255,
    verbose_name = 'colname',
    blank = False)

  tablename = models.ForeignKey(Tablename,on_delete=models.CASCADE, related_name="colnames")

  def __str__(self):
    return str(self.colname)

# Create your models here.
class Task(models.Model):

  class Meta:
    verbose_name = 'task'
    verbose_name_plural = 'tasks'

  title = models.CharField(
    max_length = 50,
    verbose_name = 'title',
    blank = False)

  description = models.TextField(
    verbose_name = 'description',
    blank = True)

  prerequisite = models.ForeignKey(
    Quiz,
    verbose_name = 'prerequisite',
    blank = True,
    null = True)

  num_posts = models.PositiveIntegerField(validators=[MinValueValidator(1)],
    verbose_name = 'number of posts',
    blank = True)

  num_labelers = models.CharField(
    max_length = 5,
    verbose_name = 'number of labelers',
    blank = True)
  random_label = models.CharField(
    max_length=5, 
    verbose_name = 'label in random order',
    choices=CHOICES,
    )
  
  label_list = models.ManyToManyField(
    Label,
    blank = True,
    default = None,
    verbose_name = 'label list',
    editable = False
    )

  post_list = models.ManyToManyField(
    Post,   
    blank = True,
    default = None,
    verbose_name = 'post list',
    editable = False
  )

  creator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    verbose_name = 'creator',
    blank = False,
    default = None,
    null = False,
    editable = False,)

  connection = models.ForeignKey(
    Connection,
    on_delete=models.CASCADE,
    verbose_name = 'connection',
    blank = False,
    default = None,
    null = False,
    editable = False,)

  table_name = models.ForeignKey(
    Tablename,
    on_delete=models.CASCADE,
    verbose_name = 'table_name',
    blank = False,
    default = None,
    null = False,
    editable = False,)
  upload_task = models.FileField(Label,upload_to='post list', default=None, editable=False)

  def __str__(self):
    return self.title

class Participation(models.Model):

  class Meta:
    verbose_name = 'participation'
    verbose_name_plural = 'participations'
    unique_together = ('task', 'labeler')

  # seq_id = models.IntegerField(null=True, blank=True, verbose_name='seq_id'),
  task = models.ForeignKey(
    Task,
    on_delete = models.CASCADE,
    blank = False,
    default = None,
    verbose_name = 'task')

  labeler = models.TextField(
    blank = False,
    default = None,
    max_length=100, 
    verbose_name = 'labeler')

  def __str__(self):
    return '{0} | {1}'.format(self.task, self.labeler)

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(Label, upload_to='post list')
    uploaded_at = models.DateTimeField(auto_now_add=True)


