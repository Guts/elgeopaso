# Serve with Apache

Resources:

- <https://modwsgi.readthedocs.io/en/develop/installation.html>
- <https://pypi.org/project/mod-wsgi/>

## Requirements

- `apache2`
- `apache2-dev`

## 1. Retrieve module wsgi and Python paths

### Using module included into the virtualenv

```sh
# in project folder
cd /var/www/elgeopaso
source .venv/bin/activate

# install mod_wsgi Python module
python -m pip install mod-wsgi==4.7.*

# run the config command to get the directives values
mod_wsgi-express module-config
> LoadModule wsgi_module "/var/www/elgeopaso/.venv/lib/python3.10/site-packages/mod_wsgi/server/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so"
> WSGIPythonHome "/var/www/elgeopaso/.venv"
```

### Copying then using module outside

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

## 2. Edit Apache configuration

```sh
# edit Apache module wsgi loader
sudo nano /etc/apache2/mods-available/wsgi.load

# paste the line output in the previous step. For example:
LoadModule wsgi_module "/usr/lib/apache2/modules/mod_wsgi-py37.cpython-37m-x86_64-linux-gnu.so"
```

```sh
sudo nano /etc/apache2/sites-available/elpaso-ssl.conf
```

At the end, restart Apache server:

```sh
sudo service apache2 restart
```
