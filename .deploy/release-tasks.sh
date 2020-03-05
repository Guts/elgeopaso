#!/bin/bash

# apply database migrations
python manage.py migrate

# load fixtures
python manage.py loaddata ./jobs/fixtures/contracts.json
python manage.py loaddata ./jobs/fixtures/jobs.json
python manage.py loaddata ./jobs/fixtures/places.json
python manage.py loaddata ./jobs/fixtures/technos.json
python manage.py loaddata ./jobs/fixtures/sources.json

# parse rss
python manage.py rss2db
