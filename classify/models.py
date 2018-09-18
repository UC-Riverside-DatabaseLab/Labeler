from django.db import models	
from django.conf import settings
from django.forms.fields import ChoiceField
from label.models import Label
from django import forms
from django.core.validators import MinValueValidator
from task.models import Task

VEC_CHOICES = (("count", "count"), ("tfidf", "tfidf"),)
CLA_CHOICES = (("cnn", "cnn"), ("rf", "rf"), ("svm", "svm"))


# Create your models here.
class Classify(models.Model):

  class Meta:
    verbose_name = 'classification model'
    verbose_name_plural = 'classifications'

  name = models.CharField(
    max_length = 50,
    verbose_name = 'name',
    blank = False,
    unique=True)

  description = models.TextField(
    verbose_name = 'description',
    blank = True)

  vectorizer = models.CharField(
    max_length=50,
    choices=VEC_CHOICES,
    default="tfidf")

  classifier = models.CharField(
    max_length=50,
    choices=CLA_CHOICES,
    default="cnn")

  conf = models.CharField(
    max_length = 5000,
    verbose_name = 'configuration',
    blank = False)

  task = models.ForeignKey(
    Task,
    default = None,
    blank=True, 
    null=True,
    verbose_name = 'task')

  upload_task = models.FileField(
    Label,
    upload_to='post list',
    default=None,
    editable=False)

  creator = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    verbose_name = 'creator',
    blank = False,
    default = None,
    null = False,
    editable = False,
    )

  def __str__(self):
    return self.name


