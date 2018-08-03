from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .models import PostResponse, QuizResponse
from quiz.models import Quiz, AnswerKey, Answer
from task.models import Task
from post.models import Post
from label.models import Label


def create_post_response(request, task_pk, post_pk):
  if request.method == 'POST':
    task = get_object_or_404(Task, pk=task_pk)
    post = get_object_or_404(Post, pk=post_pk)
    print(request.POST)
    label_id = request.POST.get('post_' + str(post.id))
    label = get_object_or_404(Label, pk=label_id)
    post_response = PostResponse.objects.create(responder=request.user,
                                                task=task,
                                                post=post,
                                                label=label)
    return HttpResponseRedirect('/task/take_task/{}'.format(task_pk))
  else:
    return HttpResponseNotFound("No label page can be retrieved")

def create_quiz_response(request, pk):
  if request.method == 'POST':
    quiz = get_object_or_404(Quiz, pk=pk)
    post_list = quiz.post_list.all()
    post_count = len(post_list)
    if quiz.max_posts and (quiz.max_posts < len(post_list)):
      question_count = quiz.max_posts
    correct_count = 0
    for post in post_list:
      label_id = request.POST.get('post_' + str(post.id))
      label = get_object_or_404(Label, pk=label_id)
      answer_key = get_object_or_404(AnswerKey, quiz=quiz.pk)
      correct = Answer.objects.filter(answer_key=answer_key.pk, post=post.pk, label=label.pk)
      if correct:
        correct_count += 1
    quiz_response = QuizResponse.objects.create(responder=request.user,
                                                quiz=quiz,
                                                score=correct_count / post_count * 100)
    if quiz_response.score >= quiz.pass_mark:
      return HttpResponseRedirect('/quiz/quiz_success/{}'.format(quiz.pk))
    else:
      return HttpResponseRedirect('/quiz/quiz_fail/{}'.format(quiz.pk))
  else:
    return HttpResponseNotFound("No label page can be retrieved")
