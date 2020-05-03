# Sauvegarde et restauration de la base de données

La base de données en production est motorisée par PostgreSQL/PostGIS (celle de développement par SQLite3) :

```sql
elpaso=> SELECT version();
elpaso=> PostgreSQL 9.6.9 on x86_64-pc-linux-gnu (Ubuntu 9.6.9-2.pgdg16.04+1), compiled by gcc (Ubuntu 5.4.0-6ubuntu1~16.04.9) 5.4.0 20160609, 64-bit
elpaso=> SELECT PostGIS_full_version();
elpaso=> POSTGIS="2.4.4 r16526" PGSQL="96" GEOS="3.5.1-CAPI-1.9.1 r4246" PROJ="Rel. 4.9.2, 08 September 2015" GDAL="GDAL 1.11.3, released 2015/09/16" LIBXML="2.9.3" LIBJSON="0.11.99" LIBPROTOBUF="1.2.1" (core procs from "2.4.1 r16012" need upgrade) RASTER (raster procs from "2.4.1 r16012" need upgrade)
```

Les données sont de plusieurs types dans le projet :

* les offres d'emploi :
  * la version brute récupérée depuis les sources (RSS GeoRezo...)
  * la version analysée

* les données de référence qui servent à l'analyse :

  * les lieux et leurs variantes
  * les types de contrats et leurs variantes
  * les technologies et leurs variantes
  * les métiers et leurs variantes

* les contenus éditoriaux (page d'accueil, section aide...)

* les tables liées à l'administration et à Django : utilisateurs, migrations...

La base est sauvegardée :

* via des tâches planifiées liées à l'infrastructure et à l'hébergeur
* via les outils de sauvegardes et restauration intégrés à Django (voir ci-dessous)
* la base sur le serveur de développement est régulièrement synchronisée dans le dépôt via Git LFS

A l'avenir, il peut être envisagé d'utiliser [Django Smuggler](https://github.com/semente/django-smuggler) pour faciliter les opérations.

----

## Utilitaires Django

Les opérations doivent se faire dans l'environnement virtuel. Documentation de référence :

* sauvegarder : [dumpdata](https://docs.djangoproject.com/en/dev/ref/django-admin/#dumpdata)
* restaurer : [loaddata](https://docs.djangoproject.com/en/dev/ref/django-admin/#loaddata)

### Sauvegarder l'ensemble des données

Utile pour effectuer une sauvegarde complète ou bien basculer les données entre développement et production. Attention, le fichier JSON produit est lourd (~90 Mo en juin 2018).

#### Sauvegarder

```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > elgeopaso_bkp_db.json
```

#### Restaurer

```bash
python manage.py loaddata elgeopaso_bkp_db.json
```

### Sauvegarder les données de départ

Pour un usage léger, des "fixtures" des principaux éléments nécessaires pour amorcer l'usage du projet sont exportes (avec indentation optionnelle) et stockées dans le dépôt du code.

#### Sauvegarder

```bash
python manage.py dumpdata jobs.Contract jobs.ContractVariations > elgeopaso/jobs/fixtures/contracts.json
python manage.py dumpdata jobs.JobPosition jobs.JobPositionVariations > elgeopaso/jobs/fixtures/metiers.json
python manage.py dumpdata jobs.Place jobs.PlaceVariations > elgeopaso/jobs/fixtures/places.json
python manage.py dumpdata jobs.Source > elgeopaso/jobs/fixtures/sources.json
python manage.py dumpdata jobs.Technology jobs.TechnologyVariations > elgeopaso/jobs/fixtures/technos.json
python manage.py dumpdata --exclude auth.permission --exclude contenttypes cms.Article cms.Category > elgeopaso/cms/fixtures/content.json
```

#### Restaurer

```bash
python manage.py loaddata elgeopaso/jobs/fixtures/contracts.json
python manage.py loaddata elgeopaso/jobs/fixtures/metiers.json
python manage.py loaddata elgeopaso/jobs/fixtures/places.json
python manage.py loaddata elgeopaso/jobs/fixtures/sources.json
python manage.py loaddata elgeopaso/jobs/fixtures/technos.json
python manage.py loaddata elgeopaso/cms/fixtures/content.json
```
