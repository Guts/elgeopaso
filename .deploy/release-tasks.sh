#!/bin/bash

# apply database migrations
python manage.py migrate

# load fixtures
python manage.py loaddata ./elgeopaso/jobs/fixtures/contracts.json
python manage.py loaddata ./elgeopaso/jobs/fixtures/jobs.json
python manage.py loaddata ./elgeopaso/jobs/fixtures/places.json
python manage.py loaddata ./elgeopaso/jobs/fixtures/technos.json
python manage.py loaddata ./elgeopaso/jobs/fixtures/sources.json

# parse rss
python manage.py rss2db
python manage.py map_builder

# launch server
# [[ -n $USE_DOCKER ]] && python manage.py runserver_plus 0.0.0.0:8000
