from django.contrib import admin

from .models import Post

class PostAdmin(admin.ModelAdmin):
	list_display = ('content', 'author', )
	search_fields = ('content', 'author', )

