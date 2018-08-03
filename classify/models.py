from django.db import models	
from django.conf import settings
from django.forms.fields import ChoiceField

#from label.models import Label1
#from label.models import Label
#from post.models import Post
#from quiz.models import Quiz
#from participation.models import Participation

from django import forms 
from django.core.validators import MinValueValidator


CHOICES = (('T', 'True'),('F', 'False'),)



# Create your models here.
class Classify(models.Model):

	class Meta:
		verbose_name = 'classification model'
		verbose_name_plural = 'classifications'

	name = models.CharField(
		max_length = 50,
		verbose_name = 'name',
		blank = False)

	description = models.TextField(
		verbose_name = 'description',
		blank = True)

#	prerequisite = models.ForeignKey(
#		Quiz,
#		verbose_name = 'prerequisite',
#		blank = True,
#		null = True)

	#num_posts = models.PositiveIntegerField(validators=[MinValueValidator(1)],
#		max_length = 5,
#		min_value = 1,
		#IntegerField(
#		min_value=0, widget=NumberInput(attrs={'min': 5, 'max': 20}),
		
		#help_text = 'no negative numbers!',
	#	verbose_name = 'number of posts',
	#	blank = True)

#	num_labelers = models.CharField(
#		max_length = 5,
#		verbose_name = 'number of labelers',
#		blank = True)
#	random_label = models.CharField(
#		max_length=5, 
#		verbose_name = 'label in random order',
#		choices=CHOICES,
#		)
	
#	participating_coders = models.TextField(
#		participation, 
#                verbose_name = 'participating coders',
#                blank = True)

	#label_list = models.ManyToManyField(
	#	Label,#.objects.filter(content__in=[Label.objects.all()]).distinct(),
	#	blank = True,
	#	default = None,
	#	verbose_name = 'label list',
	#	editable = False
	#	)
#	upload_file = models.FileField(Label,upload_to='post list')

#	post_li = models.FileField(
#		Label,
#		upload_to = 'post list')
#	uploaded_at = models.DateTimeField(auto_now_add=True)

	#post_list = models.ManyToManyField(
	#	Post,		
	#	blank = True,
	#	default = None,
	#	verbose_name = 'post list',
	#		print (Task.objects.filter( task.post_id = self.id ))
	#	limit_choices_to = { list(Task.objects.filter( task.post_id = self.id ))}
	#	editable = False
	#)

	

	creator = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete = models.CASCADE,
		verbose_name = 'creator',
		blank = False,
		default = None,
		null = False,
		editable = False,
	)

	#upload_task = models.FileField(Label,upload_to='post list', default=None, editable=False)

	def __str__(self):
		return self.name

#class Participation(models.Model):

#	class Meta:
#		verbose_name = 'participation'
#		verbose_name_plural = 'participations'
#		unique_together = ('task', 'labeler')

#	task = models.ForeignKey(
#		Task,
#		on_delete = models.CASCADE,
#		blank = False,
#		default = None,
#		verbose_name = 'task')

#	labeler = models.TextField(
#		blank = False,
#		default = None,
#		max_length=100, 
#		verbose_name = 'labeler')

#	def __str__(self):
#		return '{0} | {1}'.format(self.task, self.labeler)

#class Document(models.Model):
 #   description = models.CharField(max_length=255, blank=True)
  #  document = models.FileField(Label, upload_to='post list')
   # uploaded_at = models.DateTimeField(auto_now_add=True)


