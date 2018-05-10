from django.contrib import admin

from .models import Label

# Register your models here.
class LabelAdmin(admin.ModelAdmin):
	list_display = ('content', )
	search_fields = ('content', )

#admin.site.register(Label, LabelAdmin)
