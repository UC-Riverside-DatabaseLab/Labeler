from django.db import models
from django.conf import settings

class Post(models.Model):

  class Meta:
    verbose_name = 'post'
    verbose_name_plural = 'posts'

  db_id = models.IntegerField(null=True, blank=True, verbose_name='db_id')
  content = models.CharField(
    max_length=1000,
    blank=False,
    verbose_name='post')

  author = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    verbose_name='creator',
    blank=False,
    default=None,
    null=False)

  def __str__(self):
    return self.content

class Post1(models.Model):

  class Meta:
    verbose_name = 'post1'
    verbose_name_plural = 'posts1'

  db_id = models.IntegerField(null=True, blank=True, verbose_name='db_id')
  content = models.CharField(
          max_length=1000,
          blank=False,
          verbose_name='post1')

  author = models.ForeignKey(
          settings.AUTH_USER_MODEL,
          on_delete=models.CASCADE,
          verbose_name='creator',
          blank=False,
          default=None,
          null=False)

  def __str__(self):
    return self.content

