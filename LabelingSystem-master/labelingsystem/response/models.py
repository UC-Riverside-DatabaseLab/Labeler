from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator
from label.models import Label
from task.models import Task
from quiz.models import Quiz
from post.models import Post

# Create your models here.
class PostResponse(models.Model):

	class Meta:
		verbose_name = 'post response'
		verbose_name_plural = 'post responses'

	responder = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete = models.CASCADE,
		blank = False,
		default = None,
		verbose_name = 'responder')

	task = models.ForeignKey(
		Task,
		on_delete = models.CASCADE,
		blank = False,
		default = None,
		verbose_name = 'task')

	post = models.ForeignKey(
		Post,
		on_delete = models.CASCADE,
		blank = False,
		default = None,
		verbose_name = 'post')

	label = models.ForeignKey(
		Label,
		on_delete = models.CASCADE,
		blank = False,
		default = None,
		verbose_name = 'label')

	timestamp = models.DateTimeField(
		auto_now_add = True)

	def __str__(self):
		return '{0} | {1}'.format(self.post, self.responder)

class QuizResponse(models.Model):

	class Meta:
		verbose_name = 'quiz response'
		verbose_name_plural = 'quiz responses'

	responder = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete = models.CASCADE,
		blank = False,
		default = None,
		verbose_name = 'responder')

	quiz = models.ForeignKey(
		Quiz,
		on_delete = models.CASCADE,
		blank = False,
		default = None,
		verbose_name = 'quiz')

	score = models.PositiveIntegerField(
		default = 0,
		validators = [MaxValueValidator(100)])

	timestamp = models.DateTimeField(
		auto_now_add = True)

	def __str__(self):
		return '{0} | {1}'.format(self.quiz, self.responder)