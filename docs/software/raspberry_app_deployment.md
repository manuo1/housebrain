# Déploiement de HouseBrain sur Raspberry Pi

## Prérequis

### Matériel nécessaire
- Raspberry Pi 3 B+ (ou supérieur)
- Support de démarrage : clé USB ou SSD via adaptateur USB, avec Raspberry Pi OS Lite (64-bit) déjà flashé (voir `raspberry_install.md`)
- Alimentation 5V 2.5A minimum
- Carte lecture Téléinfo (compteur Linky) - voir `docs/hardware/teleinfo_branchement.md`
- Carte pilotage fil pilote (MCP23017 via I2C) - documentation en cours

### Réseau
- IP fixe locale recommandée (réservation DHCP côté box)
- Si accès externe souhaité : nom de domaine pointant vers votre IP publique, ports 80 et 443 redirigés vers le Pi sur votre box
- Accès SSH au Raspberry Pi

---

## Configuration matérielle : rien à faire manuellement

I2C, UART (Téléinfo) et Bluetooth sont désormais activés **automatiquement** par le
script de déploiement (module `00_hardware_preflight.sh`, via `raspi-config
nonint`). Aucune manipulation `raspi-config` à faire à la main avant de démarrer.

Si un redémarrage est nécessaire pour que ces changements prennent effet (le cas
sur une image toute fraîche), le script s'arrête de lui-même avec un message clair
demandant de redémarrer puis de relancer `deploy.sh` — voir plus bas.

---

## Déploiement initial

### 1. Connexion SSH

```bash
ssh admin@housebrain
```

### 2. Installer git (absent par défaut sur l'image Lite)

```bash
sudo apt update
sudo apt install -y git
```

### 3. Clonage du projet

Cette étape reste manuelle : le script de déploiement vit dans le repo lui-même,
il ne peut donc pas se cloner tout seul avant d'exister sur le disque.

```bash
cd /home/admin
git clone https://github.com/manuo1/housebrain.git
```

### 4. Exécution du script de déploiement

```bash
bash /home/admin/housebrain/backend/deployment/scripts/deploy.sh
```

Le script rejoue automatiquement, dans l'ordre, tous les modules de
`backend/deployment/scripts/deploy_parts/` (chacun vérifie l'état réel avant
d'agir - rien n'est fait deux fois) :

1. Préflight matériel (I2C, UART, Bluetooth, groupes utilisateur)
2. Logs persistants (journald)
3. Mise à jour système + installation des dépendances (Python, Nginx, Redis...)
4. Configuration Nginx
5. Création de l'environnement virtuel Python + installation des dépendances
6. Configuration Gunicorn
7. Génération/mise à jour du fichier `.env`
8. Migrations Django + collecte des fichiers statiques
9. Configuration Redis
10. Configuration des listeners Téléinfo et Bluetooth
11. Permissions
12. Création du superutilisateur Django (si aucun n'existe déjà)
13. Timer systemd (tâches périodiques)
14. Frontend fallback (temporaire, seulement si aucun frontend n'est encore déployé)
15. Installation de Node.js (si absent)
16. Build et déploiement du frontend React
17. Certificat HTTPS (Certbot) - voir section dédiée ci-dessous
99. Vérification finale (services actifs, application accessible, fichiers essentiels présents)

**Si le module de préflight matériel demande un redémarrage** (message explicite
à l'écran), redémarre puis relance simplement la même commande :

```bash
sudo reboot
# puis, une fois reconnecté :
bash /home/admin/housebrain/backend/deployment/scripts/deploy.sh
```

Le script est idempotent : tout ce qui a déjà été fait ne sera pas refait.

### 5. Création du superutilisateur Django

Au premier déploiement (aucun superutilisateur n'existe encore), tu seras invité à
en créer un :
```
Username: admin
Email: votre-email@example.com
Password: ********
```
Aux déploiements/updates suivants, cette étape est automatiquement ignorée.

---

## HTTPS : automatique si configuré

Si tu veux un accès externe en HTTPS, renseigne dans `/home/admin/housebrain/backend/.env` :

```bash
DOMAINS=housebrain.tondomaine.fr
CERTBOT_EMAIL=ton@email.fr
```

Le module `17_configure_certbot.sh` s'occupe ensuite de tout, à chaque déploiement
ou mise à jour : installation de Certbot, obtention/renouvellement du certificat,
application du bloc HTTPS dans Nginx et de la redirection HTTP→HTTPS. Rien à faire
à la main.

Si `DOMAINS` n'est pas configuré (ou laissé à la valeur d'exemple), ce module est
simplement ignoré : l'application reste utilisable en HTTP sur le réseau local.

Pour le détail de ce qui se passe sous le capot, le contexte DNS/Django, et du
troubleshooting plus poussé (SSL Labs, headers de sécurité...), voir
`raspberry_https_setup.md`.

---

## Accès à l'application

- Interface web : `https://housebrain.emmanuel-oudot.fr/` (ou en HTTP via l'IP locale si pas de domaine configuré)
- Admin Django : `.../backend/admin/`
- API : `.../api/`

Remplace `housebrain.emmanuel-oudot.fr` par ton propre domaine.

---

## Services déployés

| Service | Description | Vérification |
|---------|-------------|--------------|
| nginx | Serveur web (frontend + reverse proxy) | `sudo systemctl status nginx` |
| gunicorn | Serveur d'application Django | `sudo systemctl status gunicorn` |
| redis-server | Cache et pub/sub | `sudo systemctl status redis-server` |
| teleinfo-listener | Lecture compteur Linky | `sudo systemctl status teleinfo-listener` |
| bluetooth-listener | Communication Bluetooth | `sudo systemctl status bluetooth-listener` |
| housebrain-periodic.timer | Tâches périodiques (1 min) | `sudo systemctl status housebrain-periodic.timer` |
| certbot.timer | Renouvellement HTTPS automatique | `sudo systemctl status certbot.timer` |

---

## Configuration avancée

### Variables d'environnement (.env)

Le fichier `/home/admin/housebrain/backend/.env` est généré automatiquement s'il
n'existe pas, et contient :

```bash
SECRET_KEY=<généré-automatiquement>
DEBUG=False
ENVIRONMENT=production
SERIAL_PORT=/dev/ttyS0
LOCAL_IP=<détecté-automatiquement, mis à jour à chaque déploiement>
PUBLIC_IP=<détecté-automatiquement, mis à jour à chaque déploiement>
DOMAINS=<à configurer manuellement pour activer HTTPS>
CERTBOT_EMAIL=<requis si DOMAINS est configuré>
UNPLUGGED_MODE=False  # True = mode dev sans matériel
```

### Mode développement sans matériel

Si tu développes sans Raspberry Pi physique, active le mode "unplugged" :
```bash
UNPLUGGED_MODE=True
```
Cela désactive les interactions avec le GPIO, MCP23017, et le port série.

---

## Dépannage

### Vérifier les logs

```bash
sudo journalctl -u gunicorn -f
sudo journalctl -u teleinfo-listener -f
sudo journalctl -u bluetooth-listener -f
```
Voir aussi `see_logs.md` pour l'usage complet de journald (logs persistants,
filtrage, métriques système).

### Redémarrer les services

Voir le guide : `docs/software/restart_services.md`

---

## Documentation complémentaire

- `raspberry_install.md` - Installation initiale du Raspberry Pi
- `raspberry_app_update.md` - Mise à jour de l'application
- `raspberry_https_setup.md` - Détails HTTPS/Certbot et troubleshooting avancé
- `see_logs.md` - Consultation des logs
- `restart_services.md` - Redémarrage des services

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Juillet 2026
Testé sur : Raspberry Pi 3 B+ - Raspberry Pi OS Lite (64-bit) - Django 5.2
