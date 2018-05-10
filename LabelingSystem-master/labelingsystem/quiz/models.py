from django import forms
from django.db import models
from django.core.validators import MaxValueValidator
from django.conf import settings
from label.models import Label
from post.models import Post
#from .models import Participation
from django.contrib.admin.widgets import FilteredSelectMultiple
from smart_selects.db_fields import ChainedForeignKey 


# Create your models here.
class Quiz(models.Model):
	
	class Meta:
		verbose_name = 'quiz'
		verbose_name_plural = 'quizzes'

	title = models.CharField(
		max_length = 50,
		verbose_name = 'title',
		blank = False)

	description = models.TextField(
		verbose_name = 'description',
		blank = True)

	max_posts = models.PositiveIntegerField(
		blank = True,
		null = True,
		verbose_name = 'max posts')

	pass_mark = models.PositiveIntegerField(
		blank = True,
		default = 0,
		verbose_name = 'pass mark',
		validators = [MaxValueValidator(100)])

	label_list = models.ManyToManyField(
		Label,
		blank = False,
		verbose_name = 'label list',
		editable = False)

	post_list = models.ManyToManyField(
		Post,
		#default = None,
		blank = True,
		verbose_name = 'post list',
		editable = False)

	#postTag = models.ForeignKey(Post)
	#label = ChainedForeignKey(
        #	Post,
        #	chained_field="postTag",
        #	chained_model_field="postTag",
        #	show_all=False,
        #	auto_choose=True,
        #	sort=True)
	
	creator = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete = models.CASCADE,
		verbose_name = 'creator',
		default = 'none',
		blank = False,
		null = False,
		editable = False,)
	upload_quiz = models.FileField(Label,upload_to='post list', default=None, editable=False)

	#creator = models.ForeignKey(
	#	settings.AUTH_USER_MODEL,
	#	on_delete = models.CASCADE,
	#	verbose_name = 'creator',
	#	default = 'none',
	#	blank = False,
	#	null = False)

	

	def __str__(self):
		return self.title

class AnswerKey(models.Model):

	class Meta:
		verbose_name = 'answer key'
		verbose_name_plural = 'answer keys'

	quiz = models.OneToOneField(
		Quiz,
		blank = False)

	def __str__(self):
		return "{} answer key".format(self.quiz)

class Answer(models.Model):

	class Meta:
		verbose_name = 'answer'
		verbose_name_plural = 'answers'

	answer_key = models.ForeignKey(
		AnswerKey,
		blank = False,
		default = None)

	post = models.ForeignKey(
		Post,
		blank = False,
		default = None)

	label = models.ForeignKey(
		Label,
		blank = False,
		default = None)

	def __str__(self):
		return '{0}, {1}'.format(self.post, self.label)



