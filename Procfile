release: python manage.py migrate; python manage.py loaddata ./Jobs/fixtures/contracts.json
web: gunicorn elgeopaso.wsgi --log-file -
