# Déploiement

## Configuration du système

> Ce guide se base sur Ubuntu Server 18.04

Avant, tout mettre à jour la liste des paquets

```bash
sudo apt update
```

### Installer Python

```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.7
```

### Installer git

```bash
sudo add-apt-repository ppa:git-core/ppa
sudo apt update
sudo apt install git
```


### Dépendances

```
sudo apt install curl build-essential python3-software-properties python3-venv python3-dev python3-pip python-software-properties python-dev python-pip libsqlite3-dev sqlite3 bzip2 libbz2-dev gunicorn nginx git build-essential tcl
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt install git-lfs

pip3 install --upgrade pip
pip3 install virtualenv --upgrade

# web app directory
mkdir -p /webapps/elpaso
# clone repository
cd /webapps/elpaso
git clone https://github.com/Guts/elpaso.git .
mkdir tmp
# COPY secrets.ini inside folder

# groups and users
sudo groupadd --system webapps
sudo useradd --system --gid webapps --shell /bin/bash --home /webapps/elpaso elpacha
sudo usermod -a -G "www-data" elpacha
sudo chown -R elpacha:www-data /webapps/elpaso/
sudo chmod -R g+w /webapps/elpaso

# virtualenv
pvernier@datamadre:/webapps/elpaso$ sudo su - elpacha
pyvenv virtenv
source ./virtenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# back to main user
exit

# open directory to other users
sudo chown -R elpacha:www-data /webapps/elpaso
sudo chgrp -R www-data /webapps/elpaso
sudo chmod -R 770 /webapps/elpaso/
sudo usermod -a -G "webapps" geoj
sudo usermod -a -G "webapps" pvernier
sudo usermod -a -G "www-data" geoj
sudo usermod -a -G "www-data" pvernier
```

----

### Gunicorn setup (HTTP server)

#### Manual serve

```bash
# back into the virtualenv as elpacha
cd /webapps/elpaso
elpacha@datamadre:~$ source virtenv/bin/activate
# Check manual serving
(virtenv) elpacha@datamadre:~$ gunicorn elpaso.wsgi:application --bind elgeopaso.fr:8443 --log-level debug
```

#### Set gunicorn start parameters

Edit/Create the file:

```bash
nano -c /webapps/elpaso/bin/gunicorn_start
```

Insert something like this:

```bash
#!/bin/bash

NAME="ElPaso_app"                                 # Name of the application
DJANGODIR=/webapps/elpaso/                        # Django project directory
SOCKFILE=/webapps/elpaso/run/gunicorn.sock        # we will communicte using this unix soc$
USER=elpacha                                      # the user to run as
GROUP=www-data                                    # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunic$
DJANGO_SETTINGS_MODULE=elpaso.settings            # which settings file should Django use
DJANGO_WSGI_MODULE=elpaso.wsgi                    # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual env
cd $DJANGODIR
source /webapps/elpaso/virtenv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
exec /webapps/elpaso/virtenv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --log-level=debug \
  --log-file=/webapps/elpaso/logs/gunicorn.log \
  --bind=unix:$SOCKFILE
#  --bind=163.172.12.190:8443
#  --bind=elgeopaso.fr:8000
```

```bash
sudo chmod u+x /webapps/elpaso/bin/gunicorn_start
```

#### Set gunicorn as a systemd service

See: [Digital Ocean tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-debian-8#create-a-gunicorn-systemd-service-file)

1. Edit/Create the file:

    ```bash
    sudo nano /etc/systemd/system/gunicorn.service
    ```

2. Insert something like this:

    ```ini
    [Unit]
    Description=gunicorn daemon
    After=network.target

    [Service]
    User=elpacha
    Group=www-data
    WorkingDirectory=/webapps/elpaso
    ExecStart=/webapps/elpaso/bin/gunicorn_start

    [Install]
    WantedBy=multi-user.target
    ```

3. Validate, start and reference (symlink)

    ```bash
    sudo systemctl start gunicorn
    sudo systemctl daemon-reload
    sudo systemctl enable gunicorn
    sudo systemctl restart gunicorn
    ```

4. Check the status

    ```bash
    sudo systemctl status gunicorn
    ```

    Output expected:

    ```bash
    ● gunicorn.service - gunicorn daemon
       Loaded: loaded (/etc/systemd/system/gunicorn.service; enabled; vendor preset: enabled)
       Active: active (running) since Tue 2017-01-10 23:10:37 CET; 26s ago
     Main PID: 7558 (gunicorn: maste)
       CGroup: /system.slice/gunicorn.service
               ├─7558 gunicorn: master [elpaso.wsgi:application]
               ├─7570 gunicorn: worker [elpaso.wsgi:application]
               ├─7571 gunicorn: worker [elpaso.wsgi:application]
               └─7572 gunicorn: worker [elpaso.wsgi:application]

    Jan 10 23:10:37 datamadre systemd[1]: Started gunicorn daemon.
    Jan 10 23:10:38 datamadre gunicorn[7558]: [2017-01-10 23:10:38 +0100] [7558] [INFO] Starting gunicorn 19.6.0
    Jan 10 23:10:38 datamadre gunicorn[7558]: [2017-01-10 23:10:38 +0100] [7558] [INFO] Listening at: unix:/webapps/elpaso/run/gunicorn.sock (7558)
    Jan 10 23:10:38 datamadre gunicorn[7558]: [2017-01-10 23:10:38 +0100] [7558] [INFO] Using worker: sync
    Jan 10 23:10:38 datamadre gunicorn[7558]: [2017-01-10 23:10:38 +0100] [7570] [INFO] Booting worker with pid: 7570
    Jan 10 23:10:38 datamadre gunicorn[7558]: [2017-01-10 23:10:38 +0100] [7571] [INFO] Booting worker with pid: 7571
    Jan 10 23:10:38 datamadre gunicorn[7558]: [2017-01-10 23:10:38 +0100] [7572] [INFO] Booting worker with pid: 7572
    ```

----

### nginx setup (reverse proxy)

#### Remove default site

1. Edit nginx configuration

    ```bash
    sudo nano -c /etc/nginx/nginx.conf
    ```

2. Comment this line:

    ```ini
    # include /etc/nginx/conf.d/*.conf;
    ```

#### Add webapp configuration file

1. Edit file

    ```bash
    sudo nano -c /etc/nginx/sites-available/elpaso
    ```

2. Insert something like this:

    ```nginx
    server {
            listen       80;
            server_name 163.172.42.190;
            rewrite ^(.*) http://elgeopaso.fr$1 permanent;
    }


    server {
        listen       80;
        server_name  www.elgeopaso.fr;
        rewrite ^(.*) http://elgeopaso.fr$1 permanent;
    }


    server {
        listen      80;
        server_name elgeopaso.fr;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /webapps/elpaso;
        }

        client_max_body_size 4G;
        access_log /webapps/elpaso/logs/nginx.access.log;
        error_log /webapps/elpaso/logs/nginx.error.log;

        location / {
            include proxy_params;
    #        proxy_pass http://163.172.42.190:8443;  # Pass to Gunicorn
            proxy_pass http://unix:/webapps/elpaso/run/gunicorn.sock;
            proxy_set_header X-Real-IP $remote_addr; # get real Client IP
            proxy_redirect off;
        }
    }
    ```

3. Validate, symlink and start

    ```bash
    sudo ln -s /etc/nginx/sites-available/elpaso /etc/nginx/sites-enabled/elpaso
    sudo service nginx restart
    ```

----

### Option : supervisor

1. Install

    ```bash
    sudo apt install supervisor
    ```

2. Edit/create the supervisor file

    ```bash
    sudo nano -c /etc/supervisor/conf.d/elpaso.conf
    ```

3. Insert something like this:

    ```ini
    [program:elpaso]
    command = /webapps/elpaso/bin/gunicorn_start    ; Command to start app
    user = elpacha ; User to run as
    stdout_logfile = /webapps/elpaso/logs/gunicorn_supervisor.log ; Where to write log messages
    redirect_stderr = true ; Save stderr in the same log
    environment=LANG=fr_FR.UTF-8,LC_ALL=fr_FR.UTF-8 ; Set UTF-8 as default encoding
    ```

4. Validate, update and start

    ```bash
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl status elpaso
    ```

----

## Launch analisis

```python
python manage.py rss2db
```

## SSL - Let's Encrypt

```bash
sudo certbot certonly --nginx -w /webapps/elpaso -d elgeopaso.fr -d www.elgeopaso.fr
```
