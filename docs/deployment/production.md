# Déploiement

> Ce guide se base sur Ubuntu Server 18.04 (Bionic)

## Dépendances

Avant, tout mettre à jour la liste des paquets

```bash
sudo apt update
```

### Installer Python 3.7

Par défaut c'est Python 3.6 qui est livré avec Ubuntu 18.04 Bionic. Il nous faut donc :

- installer Python 3.7
- le définir comme version par défaut lorsque l'on tape `python3`

```bash
# ajouter le dépôt dans lequel trouver Python 3.7
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.7 python3-pip
# remplacer l'alias python 3
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
```

### Installer git

On a besoin d'utiliser les versions récentes de `git`.

```bash
sudo add-apt-repository ppa:git-core/ppa
sudo apt update
sudo apt install git
```

----

## Configurer un serveur web

Choisir :

- [servir avec Apache](apache)
- [servir avec Gunicorn](gunicorn)
- [utiliser nginx](nginx)

### Service

- [utiliser supervisor](supervisor)

----

## Launch analisis

```python
python manage.py rss2db
```

## SSL - Let's Encrypt

```bash
sudo certbot certonly --nginx -w /webapps/elpaso -d elgeopaso.georezo.net -d www.elgeopaso.georezo.net
```
