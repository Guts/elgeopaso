# Generated by Django 2.2.11 on 2020-03-16 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='week',
        ),
    ]
