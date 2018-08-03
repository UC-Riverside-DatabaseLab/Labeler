from django.db import models


class Label(models.Model):

  class Meta:
    verbose_name = 'label'
    verbose_name_plural = 'labels'

  content = models.CharField(
                            max_length=1000,
                            blank=False,
                            default=None,
                            verbose_name='content'
                            )

  def __str__(self):
    return self.content

class Label1(models.Model):

  class Meta:
    verbose_name = 'label'
    verbose_name_plural = 'labels'
    
  content = models.CharField(
                            max_length=1000,
                            blank=False,
                            default=None,
                            verbose_name='content'
                            )
  def __str__(self):
    return self.content
