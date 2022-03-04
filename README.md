# Hosting Proxmox

## Prérequis

- Avoir installé `mysql`, `angular` et `flask`
- Lancer la commande `pip3 install -r requirements.txt` dans le dépot pour installer les packages requis.

## Lancer le site en local 

Pour partie `backend` : 
- exporter les variables d'environnement suivantes dans votre shell (ou `/etc/environment`) pour que le backend puisse les utiliser : 

```
KEYRING_DNS_SECRET : clé pour utiliser le ddns (ajouter / supprimer des entrées notamment)
PROXMOX_API_KEY_NAME : nom de la clé pour accéder à l'api proxmox
PROXMOX_API_KEY : clé pour utiliser l'api proxmox
PROXMOX_BACK_DB : mysql:// lien vers la db contenant le passwd, user, nom de la database et bien sûr ip de celle-ci
```
- vous ensuite devez vous rendre dans backend/ et exécuter la commande `python3 -m proxmox_api`. Le serveur se lance alors.

Pour la partie `frontend`, rendez-vous dans le dossier frontend et lancez `ng serve`.

Pour que le backend et le frontend puissent communiquer, vous devez modifier : 
- dans le frontend, modifier la variable allowedUrls: dans `app.module.ts` et public `SERVER_URL` dans `auth-service.ts` pour renseigner l'ip du backend.
