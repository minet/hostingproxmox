# Hosting Proxmox

## Prérequis

- Avoir installé `mysql`, `angular` et `flask`
- Lancer la commande `pip3 install -r requirements.txt` dans le dépot pour installer les packages requis.

## Lancer le site en local 

### Le `backend` : 
- exporter les variables d'environnement suivantes dans votre shell (ou `/etc/environment`) pour que le backend puisse les utiliser : 

```
KEYRING_DNS_SECRET : clé pour utiliser le ddns (ajouter / supprimer des entrées notamment)
PROXMOX_API_KEY_NAME : nom de la clé pour accéder à l'api proxmox
PROXMOX_API_KEY : clé pour utiliser l'api proxmox
PROXMOX_BACK_DB : mysql:// lien vers la db contenant le passwd, user, nom de la database et bien sûr ip de celle-ci
ENVIRONMENT="DEV" ou "TEST" (ou "PROD")
```
L'environnement conditionne certains composants de l'application. 
1. "PROD" est réservé à l'execution de l'application dans un environnement de production. C'est par exemple au sein de cet environment que les cron jobs s'executeront. Il est impératif que seul l'env de PROD soit en charge de ce genre d'opérations
2. "DEV" désactive certaines fonctionnalités réservées à la prod, comme les cron jobs. Mais il utilise la même pas de données la production. C'est l'environment à utiliser en local ou sur hosting-dev
3. "TEST" est l'environment utilisé pour effectuer les tests unitaires et d'intégrations du backend. Il déploie un base de donnée particulière réservée aux tests.

- vous ensuite devez vous rendre dans backend/ et exécuter la commande `python3 -m proxmox_api`. Le serveur se lance alors. *Assurez vous qu'il est joignable via le port 8080 de votre machine pour qu'il puisse être joint par le `frontend`*


### Le `frontend`
Le `frontend` calcule l'adresse du backend en fonction de l'URL à partir de laquelle il s'execute. En local, l'URL **doit** être `hosting-local.minet.net:<angular port>` *(tout autre URL entrainera l'utilisation du backend de prod).*

Vous devez donc 
1. Créer l'entrée DNS locale (`/etc/host`)  : 

``127.0.0.1 hosting-local.minet.net``

2. Lancer dans le dossier `frontend`

 ` ng serve --host=127.0.0.1 --disable-host-check`.