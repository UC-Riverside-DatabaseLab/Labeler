from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.admin.models import LogEntry
from label.models import Label
from post.models import Post
from quiz.models import Quiz
from task.models import Task, Participation
from response.models import QuizResponse, PostResponse

class Command(BaseCommand):
    help = 'Generate admin group and permissions'

    def handle(self, *args, **options):
        admin_group, created = Group.objects.get_or_create(name='Admin')

        models_with_add_permission = [
            Label, Post, Quiz, Task, Participation
        ]

        models_with_change_permission = [
            Label, Post, Quiz, Task, Participation
        ]

        models_with_delete_permission = [
            Label, Post, Quiz, Task, Participation
        ]

        models_with_view_permission = [
            Label, LogEntry, Post, Quiz, QuizResponse, Task, Participation, PostResponse, User
        ]

        for model in apps.get_models():
            ct = ContentType.objects.get_for_model(model)
            model_name = model._meta.model_name

            permissions = Permission.objects.filter(content_type=ct)
            for permission in permissions:
                admin_group.permissions.remove(permission)

                add_permission = Permission.objects.get(codename='add_%s' % model_name, content_type=ct)
                change_permission = Permission.objects.get(codename='change_%s' % model_name, content_type=ct)
                delete_permission = Permission.objects.get(codename='delete_%s' % model_name, content_type=ct)
                view_permission = Permission.objects.get(codename='view_%s' % model_name, content_type=ct)

            if(model in models_with_add_permission):
                admin_group.permissions.add(add_permission)

            if(model in models_with_change_permission):
                admin_group.permissions.add(change_permission)

            if(model in models_with_delete_permission):
                admin_group.permissions.add(delete_permission)

            if(model in models_with_view_permission):
                admin_group.permissions.add(view_permission)

