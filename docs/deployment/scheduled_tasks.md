# Tâches planifiées

Le projet repose sur certaines tâches récurrentes :

* la récupération des offres d'emploi depuis GeoRezo
* le vidage du cache
* la génération des rapports envoyés par mail
* la génération des fichiers GeoJSON pour les cartes interactives
* le renouvellement du certificat SSL par Let's Encrypt

En production, c'est [cron](https://fr.wikipedia.org/wiki/Cron) qui est utilisé.

## Paramètres de planification

Pour éditer les tâches planifiées lancées par cron avec nano :

```bash
export VISUAL=nano; crontab -e
```

Insérer :

```conf
# El Paso
@hourly cd /var/www/elgeopaso && /var/www/elgeopaso/.venv/bin/python /var/www/elgeopaso/manage.py rss2db
@daily cd /var/www/elgeopaso && /var/www/elgeopaso/.venv/bin/python /var/www/elgeopaso/manage.py clear_cache
30 23 * * 7 cd /var/www/elgeopaso && /var/www/elgeopaso/.venv/bin/python /var/www/elgeopaso/manage.py report
05 00 * * 7 cd /var/www/elgeopaso && /var/www/elgeopaso/.venv/bin/python /var/www/elgeopaso/manage.py map_builder

# Let's Encrypt
0    2    *   *   *   root   /bin/bash /home/geotribu/letsencrypt/scripts/cron.sh > /home/geotribu/log/cron/letsencrypt.log
```

Pour la syntaxe, le site [crontab.guru](https://crontab.guru/) est une bonne ressource.
