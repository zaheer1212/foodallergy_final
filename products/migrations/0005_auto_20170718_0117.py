# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 01:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='userAllergies',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
