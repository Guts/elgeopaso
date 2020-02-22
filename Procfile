release: python manage.py migrate; python manage.py loaddata ./jobs/fixtures/contracts.json
web: gunicorn elgeopaso.wsgi --log-file -
