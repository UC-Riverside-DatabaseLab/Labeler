from django.contrib import admin

from .models import Quiz, Answer, AnswerKey

class FilterUserAdmin(admin.ModelAdmin):
  def save_model(self, request, obj, form, change):
      obj.user = request.user
      obj.save()

  def get_queryset(self, request):
    qs = super(FilterUserAdmin, self).get_queryset(request)
    return qs.filter(creator=request.user)

  def has_change_permission(self, request, obj=None):
    if not obj:
      return True
    return obj.creator == request.user

class QuizAdmin(FilterUserAdmin):
  list_display = ('title', 'creator',)
  filter_horizontal = ('label_list', 'post_list')
  search_fields = ('title', )

admin.site.register(Quiz, QuizAdmin)

class AnswerInline(admin.TabularInline):
  model = Answer

class AnswerKeyAdmin(admin.ModelAdmin):
  list_display = ('quiz', )
  inlines = [AnswerInline, ]
