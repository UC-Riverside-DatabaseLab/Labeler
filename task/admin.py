from django.contrib import admin
from django.db import models
from django import forms
from .models import Task, Participation, Post, Connection


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

class TaskAdmin(FilterUserAdmin):
  list_display = ('title', 'prerequisite')
  filter_horizontal = ('post_list', 'label_list')
  search_fields = ('title', )

admin.site.register(Task, TaskAdmin)

class FilterUserAdminP(admin.ModelAdmin):

  def save_model(self, request, obj, form, change):
    obj.user = request.user
    obj.save()

  def get_queryset(self, request):
    return Task.objects.filter(creator=request.user)

  def has_change_permission(self, request, obj=None):
    if not obj:
      return True
    return obj.creator == request.user

class ParticipationAdmin(admin.ModelAdmin):
  list_display = ('task', 'labeler',)
  list_filter = ('task', 'labeler', )
  search_fields = ('task', 'labeler', )

admin.site.register(Participation, ParticipationAdmin)
