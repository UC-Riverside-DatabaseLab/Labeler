from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, FormView, DetailView
from .models import Quiz
from response.models import PostResponse
from post.models import Post
from task.models import Task
from label.models import Label
from nltk.metrics.agreement import AnnotationTask
from .forms import CreateQuizForm
import random
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()

class TakeQuizView(LoginRequiredMixin, TemplateView):
  model = Quiz
  template_name = 'quiz/take_quiz.html'

  def dispatch(self, request, *args, **kwargs):
    self.quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
    return super(TakeQuizView, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(TakeQuizView, self).get_context_data(**kwargs)
    post_list = get_list_or_404(self.quiz.post_list.all())
    random.shuffle(post_list)
    context['quiz'] = self.quiz
    context['post_list'] = post_list
    context['label_list'] = self.quiz.label_list.all()
    return context

class CreateQuizView(LoginRequiredMixin, FormView):
  model = Quiz
  form_class = CreateQuizForm
  template_name = 'quiz/create_quiz.html'
  success_url = '/quiz/create_quiz_success'

  def form_valid(self, form):
    quiz_title = form.cleaned_data['Quiz Title']
    quiz_description = form.cleaned_data['Quiz Description']
    max_posts = form.cleaned_data['Number of Questions']
    pass_mark = form.cleaned_data['Pass Mark']
    quiz_upload_file = form.cleaned_data['Upload Quiz Posts and Labels']
    quiz = form.create_quiz(quiz_title, quiz_description, max_posts, pass_mark, quiz_upload_file, self.request.user)
    return super(CreateQuizView, self).form_valid(form)

class CreateQuizSuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'quiz/create_quiz_success.html'

class QuizSuccessView(LoginRequiredMixin, TemplateView):
  model = Quiz
  template_name = 'quiz/quiz_success.html'

  def dispatch(self, request, *args, **kwargs):
    self.quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
    self.task = Task.objects.filter(prerequisite=self.quiz.pk).last()
    return super(QuizSuccessView, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(QuizSuccessView, self).get_context_data(**kwargs)
    context['quiz'] = self.quiz
    context['task'] = self.task
    return context

class QuizFailView(LoginRequiredMixin, TemplateView):
  model = Quiz
  template_name = 'quiz/quiz_fail.html'

  def dispatch(self, request, *args, **kwargs):
    self.quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
    return super(QuizFailView, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(QuizFailView, self).get_context_data(**kwargs)
    context['quiz'] = self.quiz
    return context


