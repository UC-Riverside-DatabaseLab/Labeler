from django.contrib import admin
from django.db import models
from django import forms
from .models import Classify

#class CustomerForm(forms.ModelForm): 
 #   def __init__(self, *args, **kwargs):
  #      super(CustomerForm, self).__init__(*args, **kwargs)
   #     wtf = Post.objects.filter(pk=self.instance.cat_id);
    #    w = self.fields['post_list'].widget
     #   choices = []
      #  for choice in wtf:
       #     choices.append((choice.id, choice.name))
        #w.choices = choices

class FilterUserAdmin(admin.ModelAdmin): 
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def get_queryset(self, request): 
        # For Django < 1.6, override queryset instead of get_queryset
        qs = super(FilterUserAdmin, self).get_queryset(request) 
        return qs.filter(creator=request.user)

    def has_change_permission(self, request, obj=None):
        if not obj:
            # the changelist itself
            return True
        return obj.creator == request.user

class ClassifyAdmin(FilterUserAdmin):
#    pass   # (replace this with anything else you need)
	list_display = ('name', 'description')#, 'creator')
#	filter_horizontal = ('post_list', 'label_list')
	search_fields = ('name', )
admin.site.register(Classify, ClassifyAdmin)


# Register your models here.
#class TaskAdmin(admin.ModelAdmin):
	#list_display = ('title', 'prerequisite')#, 'creator')
	#filter_horizontal = ('post_list', 'label_list')
	#filter_horizontal = ('label_list', 'post_list', ) #filter_horizontal
	#search_fields = ('title', )
#	def queryset(self, request):
#        """Limit Pages to those that belong to the request's user."""
	#	qs = super(TaskAdmin, self).queryset(request)
		#if request.user.is_superuser:
            # It is mine, all mine. Just return everything.
#		if request.user = 'creator':
#	list_display = ('title', 'prerequisite')#, 'creator')
#	search_fields = ('title', )
	#	return qs
        # Now we just add an extra filter on the queryset and
        # we're done. Assumption: Page.owner is a foreignkey
        # to a User.
	#	return qs.filter(owner=request.user)

#	form = PostModelForm

#admin.site.register(Task, TaskAdmin)
class FilterUserAdminP(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def get_queryset(self, request):
        # For Django < 1.6, override queryset instead of get_queryset
#        qs = .get_queryset(request)
        return Classify.objects.filter(creator=request.user)

    def has_change_permission(self, request, obj=None):
        if not obj:
            # the changelist itself
            return True
        return obj.creator == request.user
#class ParticipationAdmin(admin.ModelAdmin):
#	list_display = ('task', 'labeler',)
#	list_filter = ('task', 'labeler', )
#	search_fields = ('task', 'labeler', )



#admin.site.register(Participation, ParticipationAdmin)
