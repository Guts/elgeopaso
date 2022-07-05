# Documentation

## Prérequis

Installer les dépendances additionnelles :

```bash
python -m pip install -U -r requirements/documentation.txt
```

## Générer la documentation

```powershell
sphinx-build -b html docs docs/_build
```

Ouvrir le fichier `docs/_build/index.html` dans un navigateur.

## Rédiger avec un rendu live

```bash
sphinx-autobuild -b html docs/ docs/_build
```

Ouvrir <http://localhost:8000>.
