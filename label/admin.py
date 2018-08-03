from django.contrib import admin
from .models import Label

class LabelAdmin(admin.ModelAdmin):
	list_display = ('content', )
	search_fields = ('content', )

