# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-25 12:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_featured'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='featured',
            name='featured_product',
        ),
    ]