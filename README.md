# Hosting Proxmox

Contributeurs : 
- [Dzenan Cindrak](https://github.com/DzeCin)
- [Jules Gonzales](https://github.com/Seberus1)
- [Nathan Stchepinsky](https://github.com/SeaweedbrainCY)
- [Gustave Beauvallet](https://github.com/getorochied)
- [Alexandre Naizondard](https://github.com/FirstThunderbolt)

## Présentation
Hosting est la plateforme d'hébergement cloud proposée gratuitement par l'[Association MiNET](https://minet.net) à ses adhérents. 

Ce code open source reprend la totalité du code de l'application web [hosting.minet.net](https://minet.net). 

## ✅ Status du Projet
Le projet utilise maintenant **Connexion 3.x** avec Flask et Angular 14. Toutes les migrations et corrections ont été appliquées :

- ✅ **Backend API** : Migration Connexion 2.x → 3.x terminée
- ✅ **Tests** : 55/55 tests unit
- ✅ **CI/CD Pipeline** : Pipeline GitLab CI/CD complètement fonctionnel
- ✅ **VM Creation** : Problème de hang résolu via correction des threads SQLAlchemy
- ✅ **Framework** : Compatibilité ASGI/Starlette intégrée
- ✅ **Test Environment** : MockProxmoxAPI implémenté pour les tests unitaires

## Prérequis
### Global
- Avoir installé `mysql`, `angular` et `flask`
- Python 3.8+ (testé avec Python 3.13)
- Node.js et npm pour le frontend Angular
### Backend
Se placer dans `backend/`
- Créer un environment virtuel `python3 -m venv .venv` et l'activer `source .venv/bin/activate`
- **Recommandé** : Utiliser `uv` pour une gestion plus rapide des dépendances : `pip install uv`
- Lancer la commande `uv sync` ou `pip3 install -r requirements.txt` dans le dépôt pour installer les packages requis.

**Note** : Le backend utilise maintenant **Connexion 3.x** avec Flask et ASGI. Les tests ont été mis à jour pour utiliser l'interface Starlette.

### Définir les différents secrets 
Dans `.env`, à la racine du projet : 
```properties
KEYRING_DNS_SECRET="<KEYRING_DNS_SECRET>"
PROXMOX_API_KEY_NAME="<PROXMOX_API_KEY_NAME>"
PROXMOX_API_KEY="<PROXMOX_API_KEY>"
PROXMOX_BACK_DB="<PROXMOX_BACK_DB>"
ADH6_API_KEY="<ADH6_API_KEY>"
PROXMOX_BACK_DB_DEV="<PROXMOX_BACK_DB_DEV>"
PROXMOX_HOST=<IP_PROXMOX_HOST>
MAIN_DNS_SERVER_IP=<IP_DNS_HOSTING>
LIST_NAME_NODES="<NODES_NAMES>"
PROXMOX_STORAGE="<STORAGE_NAME>"
ENVIRONMENT="DEV"
```

**Note importante** : Le fichier `.env` utilise le format `KEY=value` (sans `export`) contrairement à l'exemple bash ci-dessus.

#### Où trouver ces valeurs ?



Ces valeurs doivent vous êtes fournies par les maintainers actuels et dépendent de l'infrastructure.

L'environnement conditionne certains composants de l'application. 
1. `PROD` est réservé à l'execution de l'application dans un environnement de production. C'est par exemple au sein de cet environment que les cron jobs s'executeront. Il est impératif que seul l'env de PROD soit en charge de ce genre d'opérations
2. `DEV` désactive certaines fonctionnalités réservées à la prod, comme les cron jobs. Mais il utilise la même pas de données la production. C'est l'environment à utiliser en local ou sur hosting-dev
3. `TEST` est l'environment utilisé pour effectuer les tests unitaires et d'intégrations du backend. Il déploie un base de donnée particulière réservée aux tests.
## Lancer le site en local 



### Makefile
Un makefile permet de lancer le site aisément : 
- `make` pour lancer le serveur web et l'API
- `make run_server` pour lancer l'API seulement
- `make run_frontend` pour lancer le frontend



### Le `backend`/API à la main: 

1. Charger les variables d'environnement `source .env`
2. Rendez vous dans `backend/` et chargez l'environnement virtuel python : `source .venv/bin/activate`
3. Exécutez la commande `uv run python3 -m proxmox_api` (ou `python3 -m proxmox_api` si vous n'utilisez pas uv). Le serveur se lance alors. *Assurez vous qu'il est joignable via le port 8080 de votre machine pour qu'il puisse être joint par le `frontend`*

### Tests
Pour lancer les tests du backend :
```bash
cd backend/
# Tests unitaires spécifiques
uv run pytest test/test_default_controller.py -v
# Tests d'intégration (exclus du CI/CD)
uv run pytest test/integration/ -v
# Tous les tests (55 tests au total, 41% de couverture)
uv run pytest test/ -v --ignore=test/integration/
# Avec rapport de couverture
uv run pytest test/ -v --ignore=test/integration/ --cov=proxmox_api --cov-report=html
```


### Le `frontend`
Le `frontend` calcule l'adresse du backend en fonction de l'URL à partir de laquelle il s'execute. En local, l'URL **doit** être `hosting-local.minet.net:<angular port>` *(tout autre URL entrainera l'utilisation du backend de prod).*

Vous devez donc 
1. Créer l'entrée DNS locale (`/etc/host`)  : 

``127.0.0.1 hosting-local.minet.net``

2. Lancer dans le dossier `frontend`

 ` npm install `

3. Puis

 `ng serve --host=127.0.0.1 --disable-host-check`.

 ## Licence 
 La totalité du code source est régis par la Licence [AGPL-3.0](https://github.com/minet/hostingproxmox/blob/master/LICENSE). 

 Il est écrit par et pour l'Association 1901 : MiNET.

 Ce service est hébergé par MiNET sur ses serveurs en France.

 ## Contact et sécurité
 Pour tout report de vulnérabilité ou demande légale, merci de s'adresser à l'adresse mail webmaster[at]minet.net.

 Une clé PGP pourra vous être fournie en cas de vulnérabilité trouvée.

## Mentions légales
[Voir les mentions légales](https://hosting.minet.net/legal)