# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-12-04 18:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0045_auto_20171130_2249'),
    ]

    operations = [
        migrations.AddField(
            model_name='escuela',
            name='observaciones',
            field=models.CharField(blank=True, default=None, max_length=1024, null=True),
        ),
    ]