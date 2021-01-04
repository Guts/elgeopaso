# Git Flow

Le projet s'appuie sur l'intégration d'Heroku avec Github pour déployer des versions de test/développement et de pré-production :

- [les *Review Apps*](https://devcenter.heroku.com/articles/github-integration-review-apps#changes) : des déploiements temporaires correspondant à une *Pull Request*
- [une application gratuite](https://www.heroku.com/pricing) : déploiement automatisé à partir de `master` sur <https://elgeopaso-dev.herokuapp.com/>.

## Branches

- `origin/master` :
  - branche principale
  - correspond à la pré-production
  - *pull request* obligatoire : aucun commit ne peut être poussé directement
  - automatiquement déployée sur Heroku : <https://elgeopaso-dev.herokuapp.com/>

- `origin/develop` :
  - branche générique pour le développement actif

- `origin/housekeeping` :
  - branche dédiée aux opérations courantes de maintenance, mise à jour des dépendances, etc.

## Processus type

1. Une nouvelle branche est créée ou une existante est utilisée

2. Des changements sont apportés dans cette branche et poussés vers la branche principale (master) via une pull-request. Un déploiement temporaire est effectué sur une URL mi-aléatoire. Exemple :

    - travail sur l'amélioration de la lecture du RSS pour gérer les problèmes d'encodage : <https://github.com/Guts/elgeopaso/pull/9>
    - déploiement temporaire correspondant : <https://el-geo-paso-rss-parser-xxsprem.herokuapp.com/> - l'URL est indiqué sur la pull request

3. Une fois les changements achevés et validés, ils sont fusionnés dans la branche principale (*merged*) qui est automatiquement déployée sur Heroku : <https://elgeopaso-dev.herokuapp.com/>

4. Lorsqu'une nouvelle version est finalisée, un [numéro de version](../global/product_life.md) est ajouté via un `git tag`.

> Pour comprendre l'étiquetage des commits, voir <https://git-scm.com/book/en/v2/Git-Basics-Tagging> ou [Divers - Utilitaires](../misc/miscellaneous.md).

----

## Déploiement

### Depuis le serveur de production

#### Configuration initiale de Git

1. S'ajouter aux utilisateurs

    ```bash
    sudo adduser geotribu users
    ```

2. Générer une paire de clés SSH :

    ```bash
    ssh-keygen -f ~/.ssh/git_elgeopaso_rsa -t rsa -b 4096 -C "elpaso@georezo.net"
    ```

3. Ajouter la clé publique dans la partie **Deploy keys** du dépôt en lecture seule : <https://github.com/Guts/elgeopaso/settings/keys>.

> Voir la documentation officielle de GitHub : <https://developer.github.com/v3/guides/managing-deploy-keys/#deploy-keys>

#### Configurer le dossier de destination

On utilise le fork du [script de François Romain](https://gist.github.com/francoisromain/58cabf43c2977e48ef0804848dee46c3) :

```bash
# récupérer le script
mkdir ~/scripts
cd ~/scripts
git clone git@gist.github.com:36672e8730244764b4a047f6584bd66d.git git-flow-deploy

# lancer le script
source git-flow-deploy/project-create elgeopaso

# modifier le git hook
cd /srv/git/elgeopaso.git/hooks/
sudo nano post-receive

# copier le contenu du fichier : .deploy/git-hooks/post-receive
```

Ressources :

- [le fichier du hook post-receive dans le dépôt](https://github.com/Guts/elgeopaso/blob/master/.deploy/git-hooks/post-receive.sh)
- Voir le billet de blog lié : <https://medium.com/@francoisromain/vps-deploy-with-git-fea605f1303b>

### Depuis la machine locale

Ajouter le dépôt distant correspondant au serveur :

```powershell
git remote add deploy-prod ssh://geotribu@elgeopaso.georezo.net/srv/git/elgeopaso.git/
```

Pour publier (par exemple depuis master) :

```powershell
git push --follow-tags deploy-prod master
```
