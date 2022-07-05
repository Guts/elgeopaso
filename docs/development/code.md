# Structure du code

## Règles

### Nommage des dossiers et fichiers

* les sous-dossiers/fichiers précédés par un `.` sont liés au développement

### Formatage du code

Le projet s'appuie sur [black](https://github.com/python/black) pour formater automatiquement le code source. Un ensemble de `git hooks` peut également être utilisé afin de formater le code à chaque commit, via [pre-commit](https://pre-commit.com) en installant les _hooks_ configurés dans le fichier `.pre-commit-config.yaml` :

```python
# installer les hooks
pre-commit install
# les exécuter manuellement
pre-commit run -a
```

----

## Dossier `.vscode`

Configuration pour l'éditeur Visual Studio Code :

* extensions recommandées (`extensions.json`)
* tâches (`tasks.json`)
* paramètres d'environnement de travail sur le projet (tests, etc.) (`settings.json`)
* paramètres de débogage (`launch.json`)

----

## Dossier `tests`

Tests unitaires et leurs éventuelles [*fixtures*](https://fr.wikipedia.org/wiki/Test_fixture).

----

## Divers

* `example.env`: modèle de fichier d'environnement
* `setup.cfg` : configuration de l'environnement Python
