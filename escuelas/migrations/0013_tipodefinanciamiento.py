# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-09 14:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0012_auto_20170609_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDeFinanciamiento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'tiposDeFinanciamiento',
                'verbose_name_plural': 'tiposDeFinanciamiento',
            },
        ),
    ]
