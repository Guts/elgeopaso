# Utiliser Gunicorn pour servir le site

## Installer

```bash
sudo apt update
sudo apt install gunicorn
```

## Tester manuellement

```bash
# back into the virtualenv as elpacha
cd /webapps/elpaso
elpacha@datamadre:~$ source virtenv/bin/activate
# Check manual serving
(virtenv) elpacha@datamadre:~$ gunicorn elpaso.wsgi:application --bind elgeopaso.georezo.net:8443 --log-level debug
```

----

## Définir les paramètres de démarrage

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
#  --bind=elgeopaso.georezo.net:8000
```

```bash
sudo chmod u+x /webapps/elpaso/bin/gunicorn_start
```

## Démarrer Gunicorn en tant que service (_systemd_)

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
