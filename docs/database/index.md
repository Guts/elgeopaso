# Administration de la base de données

## Configuration initiale

Ouvrir la session super-admin avec l'utilisateur `postgres` (créé par défaut lors de l'installation) :

```bash
sudo -u postgres psql

psql (12.2 (Ubuntu 12.2-2.pgdg16.04+1), serveur 9.6.17)
Saisissez « help » pour l'aide.

postgres=#
```

Une fois dans l'invite de commandes `psql` :

```psql
CREATE DATABASE elgeopaso;
```

Créer l'utilisateur avec les options recommandées pour Django :

```psql
CREATE USER "elgeopaso-db-uzr";
ALTER ROLE "elgeopaso-db-uzr" SET client_encoding TO 'utf8';
ALTER ROLE "elgeopaso-db-uzr" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "elgeopaso-db-uzr" SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE elgeopaso TO "elgeopaso-db-uzr";

\password "elgeopaso-db-uzr"
```

Ressources :

* [Configuration PostgreSQL recommandée par Django](https://docs.djangoproject.com/fr/2.2/ref/databases/#postgresql-notes)
* [Doc officielle sur `ALTER ROLE` et la création protégée de mot de passe](https://docs.postgresql.fr/12/sql-alterrole.html)

----

## Opérations courantes

Après connexion en tant que super utilisateur :

```bash
sudo -u postgres psql
```

### Lister les bases

```psql
\l

                                  Liste des bases de données
    Nom    | Propriétaire | Encodage | Collationnement | Type caract. |    Droits d'accès
-----------+--------------+----------+-----------------+--------------+-----------------------
 elpaso    | postgres     | UTF8     | fr_FR.UTF-8     | fr_FR.UTF-8  | =Tc/postgres         +
           |              |          |                 |              | postgres=CTc/postgres+
           |              |          |                 |              | geotribu=CTc/postgres
 postgres  | postgres     | UTF8     | fr_FR.UTF-8     | fr_FR.UTF-8  |
 template0 | postgres     | UTF8     | fr_FR.UTF-8     | fr_FR.UTF-8  | =c/postgres          +
           |              |          |                 |              | postgres=CTc/postgres
 template1 | postgres     | UTF8     | fr_FR.UTF-8     | fr_FR.UTF-8  | =c/postgres          +
           |              |          |                 |              | postgres=CTc/postgres
(4 lignes)
```

### Lister les utilisateurs

```psql
\du+

                                                     Liste des rôles
 Nom du rôle |                                    Attributs                                    | Membre de | Description
-------------+---------------------------------------------------------------------------------+-----------+-------------
 geotribu    |                                                                                 | {}        |
 postgres    | Superutilisateur, Créer un rôle, Créer une base, Réplication, Contournement RLS | {}        |
```
