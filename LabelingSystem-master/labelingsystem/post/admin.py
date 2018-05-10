from django.contrib import admin

from .models import Post

# Register your models here.
class PostAdmin(admin.ModelAdmin):
	list_display = ('content', 'author', )
	search_fields = ('content', 'author', )

#admin.site.register(Post, PostAdmin)

