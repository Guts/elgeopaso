# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-28 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_georezorss_to_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='georezorss',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Ajoutée le'),
        ),
        migrations.AlterField(
            model_name='georezorss',
            name='pub_date',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Publiée le'),
        ),
        migrations.AlterField(
            model_name='georezorss',
            name='updated',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Modifiée le'),
        ),
    ]
