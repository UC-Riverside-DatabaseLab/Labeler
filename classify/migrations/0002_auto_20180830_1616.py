# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-30 23:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classify',
            name='task',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='task.Task', verbose_name='task'),
        ),
    ]
