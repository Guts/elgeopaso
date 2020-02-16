#! python3
from __future__ import absolute_import, unicode_literals

###############################################################################
########### Libraries #############
###################################

# Standard library
import logging

# 3rd party modules
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

# Django project
from django.core import serializers
from .models import Offer

###############################################################################
############ Globals ##############
###################################

logger = logging.getLogger(__name__)
serial2json = serializers.get_serializer("json")

###############################################################################
############ Tasks ################
###################################

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@periodic_task(run_every=(run_every=(crontab(hour="*", minute="*", day_of_week="*"))),
			   name="some_task")
def some_task():
    print("youpi")
    logger.info('Adding youpi')


@periodic_task(run_every=(run_every=(crontab(hour="*", minute="*", day_of_week="*"))),
			   name="some_task")
@last50_task
def export_latest50():
	last50_data = Offer.objects.all().order_by('-pub_date')[:50]
	with open("/static/json/latest50.json", "w") as output_json:
    	serial2json.serialize(last50_data,
    						  stream=out)
