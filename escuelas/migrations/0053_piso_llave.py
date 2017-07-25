# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-25 13:40
from __future__ import unicode_literals

from django.db import migrations, models
import escuelas.models.piso


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0052_evento_escuela'),
    ]

    operations = [
        migrations.AddField(
            model_name='piso',
            name='llave',
            field=models.FileField(blank=True, default=None, null=True, upload_to=escuelas.models.piso.upload_to, verbose_name=b'llave'),
        ),
    ]