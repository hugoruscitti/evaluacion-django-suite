# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-11 23:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0042_paquete_tpmdata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='escuela',
            name='tipo_de_financiamiento',
        ),
        migrations.AddField(
            model_name='escuela',
            name='tipo_de_financiamiento',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='escuelas', to='escuelas.TipoDeFinanciamiento'),
        ),
    ]
