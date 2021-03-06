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
```
- vous ensuite devez vous rendre dans backend/ et exécuter la commande `python3 -m proxmox_api`. Le serveur se lance alors. *Assurez vous qu'il est joignable via le port 8080 de votre machine pour qu'il puisse être joint par le `frontend`*


### Le `frontend`
Le `frontend` calcule l'adresse du backend en fonction de l'URL à partir de laquelle il s'execute. En local, l'URL **doit** être `hosting-local.minet.net:<angular port>` *(tout autre URL entrainera l'utilisation du backend de prod).*

Vous devez donc 
1. Créer l'entrée DNS locale (`/etc/host`)  : 

``127.0.0.1 hosting-local.minet.net``

2. Lancer dans le dossier `frontend`

 ` ng serve --host=127.0.0.1 --disable-host-check`.