# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-10-10 17:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0080_auto_20181008_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='paquete',
            name='perfil_que_solicito_el_paquete',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perfil_paquetes', to='escuelas.Perfil'),
        ),
    ]
