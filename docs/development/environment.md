# Développement

## Prérequis

### OS

#### Windows

Version 10 minimum

* activer le [sous-système Linux (WSL)](https://docs.microsoft.com/fr-fr/windows/wsl/install-win10) :
  * installer [Debian](https://www.microsoft.com/store/apps/9MSVKQC78PK6) ou Ubuntu ([16.04](https://www.microsoft.com/store/apps/9pjn388hp8c9) ou [18.04](https://www.microsoft.com/store/apps/9N9TNGVNDL3Q))
  * [initialiser l'instance](https://docs.microsoft.com/fr-fr/windows/wsl/initialize-distro)
  * installer les paquest souhaités, par exemple openssl : `sudo apt update && sudo apt upgrade && sudo apt install openssl libssl-dev`
* l'utilisation [du nouveau Terminal](https://www.microsoft.com/fr-fr/p/windows-terminal-preview/9n0dx20hk701?activetab=pivot:overviewtab) est fortement recommandée

#### Linux

Distributions compatibles :

* Debian
* Ubuntu 16.04 ou 18.04

### Logiciels

* Docker (Engine et Compose a minima)
* Python 3.10 64 bits
* PostgreSQL 12

----

## Lancer en local

> Commandes lancées sous Windows 10 avec WSL activé.

### Installation

```powershell
# create virtual env
# on Linux: python3.10 -m venv .venv
py -3.10 -m venv .venv

# enter into
.\.venv\Scripts\activate
# on Linux: source .venv/bin/activate

# upgrade install tooling
python -m pip install --upgrade pip

# install requirements
python -m pip install -U -r .\requirements\local.txt
# on Linux: python -m pip install -U -r requirements/local.txt

# download NLTK packages - please refer to `ntlk.txt`
python -m nltk.downloader punkt stopwords

# optionally, install pre-commit git-hooks
pre-commit install
```

### Configuration

Renommer le fichier `example.env` en `.env` et le compléter. Pour info, il est possible de générer une clé Django Secret en passant par OpenSSL sur WSl : `wsl -- openssl rand -base64 64` (copier/coller dans le fichier `.env`).

### Base de données

Initialiser la base de données :

```powershell
# apply migrations to database
python manage.py migrate

# create the super user
python manage.py createsuperuser
```

Pour charger des enregistrements de base (technologies, métiers, types de contrats, etc.), utiliser `loaddata` :

* voir les commandes dans le fichier de déploiement : `.deploy/release-tasks.sh`
* voir ["Restaurer les données"](backup#restaurer-1)

### Lancer

```powershell
# launch development web server
python .\manage.py runserver
# on Linux: python manage.py runserver

# alternatively, use the enhanced command from django-extensions
python .\manage.py runserver_plus
```

Ouvrir le navigateur à l'adresse indiquée dans le terminal. Par défaut : <http://localhost:8000/>.

#### Avec HTTPS

Pour développer au mieux, il est préférable de servir l'application en HTTPS. C'est possible via `runserver_plus` de Django Extensions ([voir la documentation](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html#ssl)).

```powershell
# create folder where to store certificate and key
mkdir certs
# generate SSL certificate and key
wsl -- openssl req -nodes -new -x509 -days 365 -keyout certs/serverKey.key -out certs/serverCert.cert
# on Linux: remove 'wsl -- '

# alternatively, use the enhanced command from django-extensions
python .\manage.py runserver_plus --cert-file .\certs\serverCert.cert --key-file .\certs\serverKey.key
```

Ouvrir le navigateur à l'adresse indiquée dans le terminal. Par défaut : <https://localhost:8000/>. Accepter [le risque lié aux certificats auto-signés](https://support.mozilla.org/fr/kb/comment-regler-codes-erreur-securite-sur-sites-securises?as=u&utm_source=inproduct#w_certificats-auto-signaes).

----

## Docker

### Prérequis Docker

* Docker 2.2+ ou dans le détail :
  * Docker Engine : 19.03+
  * Docker Compose 1.25+

### Configuration Docker

Renommer fichier `example.env` en `docker.env` et compléter :

```ini
# DEVELOPMENT
DJANGO_DEBUG=1
USE_DOCKER=1

# GLOBAL
DJANGO_ADMIN_URL="admin"
DJANGO_PROJECT_FOLDER="elgeopaso"
DJANGO_SECURE_SSL_REDIRECT=0
DJANGO_SETTINGS_MODULE="elgeopaso.settings.production"
WEB_CONCURRENCY=4

# SECURITY
DJANGO_SECRET_KEY="change_me_with_generated_key"
DJANGO_ALLOWED_HOSTS="localhost, 0.0.0.0, 127.0.0.1"

# EMAIL
REPORT_RECIPIENTS="elpaso@georezo.net,"
SMTP_USER="elpaso@georezo.net"
SMTP_PSWD=

# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=database
POSTGRES_PORT=5432
POSTGRES_DB=elgeopaso-dev
POSTGRES_USER=elgeopaso
POSTGRES_PASSWORD=elgeopaso
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
```

### Usage

#### Lancer l'application

```shell
docker-compose -f docker-compose.dev.yml up -d
```

Ouvrir le navigateur sur <http://localhost:8000>.

#### Données et analyses de base

Après que l'application soit lancée :

```shell
docker-compose -f docker-compose.dev.yml run --rm webapp sh .deploy/release-tasks.sh
```
