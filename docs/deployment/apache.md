# Utiliser Apache pour servir le site

Pour servir l'application avec Apache, retenir ces quelques points de vigilance :

- par défaut, Apache ne support pas [WSGI](https://wsgi.readthedocs.io/en/latest/what.html). Il faut donc utiliser le module `mod_wsgi` pour Apache.
- par défaut sur Ubuntu 18.04, ce module est compilé ave Python 3.6. **Or, il faut utiliser la version compilée avec la même version de Python que celle utilisée par l'application**.

## Prérequis

```sh
# add repo with latest Apache version
sudo add-apt-repository ppa:ondrej/apache2
# install apache and dependencies
sudo apt install apache2 apache2-dev brotli
# enable brotli module
sudo a2enmod brotli
```

## Déployer l'application Django avec le module Apache WSGI

### 1. Identifier la bonne version du module et le chemin Python

#### Installer et utiliser le module inclus dans l'environnement virtuel de l'application

```sh
# in project folder
cd /var/www/elgeopaso
source .venv/bin/activate

# install mod_wsgi Python module
python -m pip install mod-wsgi==4.7.*

# run the config command to get the directives values
mod_wsgi-express module-config
> LoadModule wsgi_module "/var/www/elgeopaso/.venv/lib/python3.7/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so"
> WSGIPythonHome "/var/www/elgeopaso/.venv"
```

#### Installer et utiliser le module directement dans Apache

```sh
# open root input
sudo su -
# in project folder
cd /var/www/elgeopaso
source .venv/bin/activate

# install mod_wsgi Python module
python -m pip install mod-wsgi==4.7.*

# run the config command to get the directives values
mod_wsgi-express install-module
> LoadModule wsgi_module "/usr/lib/apache2/modules/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so"
> WSGIPythonHome "/var/www/elgeopaso/.venv"
```

----

### 2. Mettre à jour la configuration Apache

```sh
# edit Apache module wsgi loader
sudo nano /etc/apache2/mods-available/wsgi.load

# paste the line output in the previous step. For example:
LoadModule wsgi_module "/usr/lib/apache2/modules/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so"
```

----

### 3. Enable site, reload and restart

Validate configuration syntax:

```sh
sudo apache2ctl -t
```

Enable virtual hosts:

```sh
sudo a2ensite elpaso.conf
sudo a2ensite elpaso-ssl.conf
```

At the end, restart Apache server:

```sh
sudo service apache2 restart
```

----

### 4. Générer le certificat SSL avec Let's Encrypt

Il s'agit principalement de la reproduction de la doc officielle : <https://certbot.eff.org/lets-encrypt/ubuntubionic-apache>.

```sh
# travailler dans home
mkdir ~/letsencrypt
cd ~/letsencrypt

# enregistrer le dépôt des paquets de certbot - letsencrypt
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt update

# installer le certbot
sudo apt-get install certbot python3-certbot-apache

# lancer le processus en choisiasant elgeopaso.georezo.net
sudo certbot --apache
```

Tester le renouvellement automatique :

```sh
sudo certbot renew --dry-run
```

----

## Commandes habituelles

```bash
# check full version and compilation details
apache2ctl -V

# help
apache2ctl -h

# list enabled modules
apache2ctl -M

```

----

## Resources

- [Django avec Apache et mod_wsgi](https://docs.djangoproject.com/fr/2.2/howto/deployment/wsgi/modwsgi/)
- [Déployer Apache sur Ubuntu](https://doc.ubuntu-fr.org/apache2)
- [documentation officielle du module mod_wsgi](https://modwsgi.readthedocs.io/en/develop/installation.html)
- [Le package Python correspondant au module WSGI pour Apache](https://pypi.org/project/mod-wsgi/)
- [Procédure de création d'un certificat SSL avec Let's Encrypt pour Apache](https://certbot.eff.org/lets-encrypt/ubuntuxenial-apache)
- [Outil de génération de configuration Apache par Mozilla](https://ssl-config.mozilla.org/)
