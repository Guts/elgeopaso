# Utilitaires et divers

## Etiqueter un commit pour publier une version

Commande exemple dans un terminal *git*, où `XXXXXX` est la signature (hash) du commit :

```git
git tag -a 1.5.0 XXXXXXX -m "Mars 2020"
git push origin 1.5.0
```

En cas d'erreur, il est possible de renommer une étiquette :

```git
git tag new old
git tag -d old
git push origin :refs/tags/old
git push --tags
```

----

## Générer le modèle graphique de la base de données

[Graph models, inclus dans la boîte à outils Django Extensions](http://django-extensions.readthedocs.io/en/latest/graph_models.html), permet de générer un graphique récapitulatif de la base de données :

![DB Model Graph](https://raw.githubusercontent.com/Guts/elpaso/master/docs/elpaso_db_models_graph.png)

### Dépendances

Il s'appuie sur l'une des 2 bibliohtèques :

* pydot - celle que nous utilisons, car bien plus légère
* pygraphviz

```bash
sudo apt install pkg-config python-pydot graphviz graphviz-dev
```

Puis, dans l'environnement virtuel du projet :

```bash
source ./virtenv/bin/activate
pip install pydot
```

> Note : il peut être nécessaire d'installer une version spécifique de pyparsing, une dépendance de pydot :
> `pip install pyparsing==1.5.7`

### Génération

Dans l'environnement virtuel du projet :

```bash
python manage.py graph_models --pydot -a -g -o docs/elpaso_db_models_graph.png
```
