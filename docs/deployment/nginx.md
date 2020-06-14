# Utiliser nginx en tant que reverse proxy

## Installer

```bash
sudo apt update
sudo apt install nginx
```

## Remplacer le site par défault

1. Edit nginx configuration

    ```bash
    sudo nano -c /etc/nginx/nginx.conf
    ```

2. Comment this line:

    ```ini
    # include /etc/nginx/conf.d/*.conf;
    ```

## Configurer l'application

1. Edit file

    ```bash
    sudo nano -c /etc/nginx/sites-available/elgeopaso
    ```

2. Insert something like this:

    ```nginx
    server {
            listen       80;
            server_name 163.172.42.190;
            rewrite ^(.*) http://elgeopaso.georezo.net$1 permanent;
    }


    server {
        listen       80;
        server_name  www.elgeopaso.georezo.net;
        rewrite ^(.*) http://elgeopaso.georezo.net$1 permanent;
    }


    server {
        listen      80;
        server_name elgeopaso.georezo.net;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /webapps/elgeopaso;
        }

        client_max_body_size 4G;
        access_log /webapps/elgeopaso/logs/nginx.access.log;
        error_log /webapps/elgeopaso/logs/nginx.error.log;

        location / {
            include proxy_params;
    #        proxy_pass http://163.172.42.190:8443;  # Pass to Gunicorn
            proxy_pass http://unix:/webapps/elgeopaso/run/gunicorn.sock;
            proxy_set_header X-Real-IP $remote_addr; # get real Client IP
            proxy_redirect off;
        }
    }
    ```

3. Validate, symlink and start

    ```bash
    sudo ln -s /etc/nginx/sites-available/elgeopaso /etc/nginx/sites-enabled/elgeopaso
    sudo service nginx restart
    ```

----
