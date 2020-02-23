release: |
    python manage.py migrate;
    python manage.py loaddata ./jobs/fixtures/contracts.json;
    python manage.py loaddata ./jobs/fixtures/places.json;
web: gunicorn elgeopaso.wsgi --log-file -
