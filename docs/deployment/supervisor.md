# Utiliser supervisor

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
