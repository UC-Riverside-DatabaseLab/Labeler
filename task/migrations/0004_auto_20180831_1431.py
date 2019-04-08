# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-31 21:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_task_table_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='connection',
            field=models.ForeignKey(blank=True, default=None, editable=False, on_delete=django.db.models.deletion.CASCADE, to='task.Connection', verbose_name='connection'),
        ),
    ]