# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-10 00:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='db_id',
            field=models.IntegerField(default=None, verbose_name='db_id'),
        ),
        migrations.AlterField(
            model_name='post1',
            name='db_id',
            field=models.IntegerField(default=None, verbose_name='db_id'),
        ),
    ]
