from django.contrib import admin

from .models import PostResponse, QuizResponse

class PostResponseAdmin(admin.ModelAdmin):
  list_display = ('responder', 'post', 'timestamp', )
  list_filter = ('responder', 'post', )
  search_fields = ('responder', 'post', )

class QuizResponseAdmin(admin.ModelAdmin):
  list_display = ('responder', 'quiz', 'score', 'timestamp', )
  list_filter = ('responder', 'quiz', 'score')
  search_fields = ('responder', 'quiz', )
