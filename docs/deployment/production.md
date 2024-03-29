# Déploiement

> Ce guide se base sur Ubuntu Server 18.04 (Bionic)

## Dépendances

Avant, tout mettre à jour la liste des paquets

```bash
sudo apt update
```

### Installer Python 3.10

Par défaut c'est Python 3.6 qui est livré avec Ubuntu 18.04 Bionic. Il nous faut donc :

- installer Python 3.10
- le définir comme version par défaut lorsque l'on tape `python3`

```bash
# ajouter le dépôt dans lequel trouver Python 3.10
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install libpq-dev python3-pip python3.10 python3.10-dev python3.10-venv
```

Au passage, on installe tout ce qu'il faut pour builder [psycopg2](https://tekshinobi.com/install-psycopg2-on-ubuntu-18-04/).

#### Personnaliser bash

Configurer `bash` pour faire correspondre `python3` à Python 3.10 :

```bash
nano ~/.bashrc
```

Ajouter les lignes en fin de fichier :

```config
# Custom python3 alias
alias python='/usr/bin/python3.10'
```

Charger la configuration :

```bash
. ~/.bashrc
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

- [servir avec Apache](apache)
