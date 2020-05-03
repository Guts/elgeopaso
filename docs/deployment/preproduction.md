# Pré-production

Le site est déployé en pré-production sur [Heroku](https://dashboard.heroku.com/apps).

## Prérequis

- compte Heroku : le niveau gratuit suffit pour un déploiement basique
- outil en ligne de commande Heroku : [CLI Heroku](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)

## Déployer

### Déploiement automatisé

L'application peut être déployée automatiquement via le fichier `app.json`.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

> Plus d'informations : <https://devcenter.heroku.com/articles/heroku-button>

### Déploiement pas à pas

> Commandes lancées sous Windows 10 avec WSL activé.

```powershell
# authenticate
heroku login

# add convenient plugin to pull/push from/to `.env` files
# https://github.com/xavdid/heroku-config
heroku plugins:install heroku-config

# create app in Europe
heroku create elgeopaso-dev --region eu

# add PostgreSQL database and schedule backup
heroku addons:create heroku-postgresql:hobby-dev --version=12
heroku pg:backups schedule --at "02:00 Europe/Paris" DATABASE_URL
# On bash, use simple quotes for the time zone: heroku pg:backups schedule --at '02:00 Europe/Paris' DATABASE_URL

# set some environment variables pointing to application's settings
heroku config:set PYTHONHASHSEED=random
heroku config:set WEB_CONCURRENCY=4
heroku config:set DJANGO_DEBUG=False
heroku config:set DJANGO_SETTINGS_MODULE=elgeopaso.settings.production
heroku config:set DJANGO_ALLOWED_HOSTS=elgeopaso-dev.herokuapp.com
heroku config:set DJANGO_ADMIN_URL=admin
heroku config:set DJANGO_SECRET_KEY=$(wsl -- openssl rand -base64 64)
# on bash: heroku config:set DJANGO_SECRET_KEY="$(openssl rand -base64 64)"

# now, let's deploy
git push heroku master:master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser --email elpaso@georezo.net
heroku run python manage.py check --deploy
heroku open
```
