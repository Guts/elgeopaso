#!/bin/bash

python manage.py dumpdata jobs.Contract jobs.ContractVariations > elgeopaso/jobs/fixtures/contracts.json
python manage.py dumpdata jobs.JobPosition jobs.JobPositionVariations > elgeopaso/jobs/fixtures/metiers.json
python manage.py dumpdata jobs.Place jobs.PlaceVariations > elgeopaso/jobs/fixtures/places.json
python manage.py dumpdata jobs.Source > elgeopaso/jobs/fixtures/sources.json
python manage.py dumpdata jobs.Technology jobs.TechnologyVariations > elgeopaso/jobs/fixtures/technos.json
python manage.py dumpdata --exclude auth.permission --exclude contenttypes cms.Article cms.Category > elgeopaso/cms/fixtures/content.json
