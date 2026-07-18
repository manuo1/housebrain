# Mise à jour de HouseBrain

Ce guide explique comment mettre à jour votre installation HouseBrain sur Raspberry Pi.

---

## Un seul script, tout est rejoué automatiquement

Il n'y a plus qu'un seul script de mise à jour, qui gère à la fois le backend et le
frontend. Pas de distinction "backend only" / "backend + frontend" : `update.sh`
récupère le dernier code, puis rejoue **tous** les modules de déploiement
(`deploy_parts/`), exactement les mêmes que ceux utilisés lors de l'installation
initiale. Chaque module est idempotent (il vérifie l'état réel avant d'agir), donc
rejouer l'intégralité de la séquence à chaque update ne casse rien et ne refait pas
de travail inutile.

Concrètement, ça veut dire qu'une simple mise à jour de code applique aussi, sans
action manuelle de ta part :
- toute modification de config système (nginx, systemd, permissions...)
- le renouvellement/réapplication du certificat HTTPS (Certbot)
- les mises à jour de paquets système (`apt upgrade`)
- la reconstruction du frontend si le code a changé

---

## Procédure

### 1. Connexion SSH

```bash
ssh admin@housebrain
```

### 2. Lancer la mise à jour

```bash
bash /home/admin/housebrain/backend/deployment/scripts/update.sh
```

### Ce que fait le script, dans l'ordre

1. **Vérifie que le repo est propre** (`git status --porcelain`). Ce Pi ne doit
   jamais avoir de modification locale — tout le code vient du repo distant. Si des
   modifs locales traînent, le script s'arrête plutôt que de les écraser
   silencieusement (voir Dépannage ci-dessous).
2. **Sauvegarde `db.sqlite3`** dans `db.sqlite3.pre-update-bak` (écrase la
   sauvegarde précédente à chaque update — un seul filet de sécurité, pas un
   historique). Sert de retour arrière rapide en cas de souci après une migration.
3. **`git pull`** : récupère le dernier code.
4. **Rejoue tous les `deploy_parts`** (`run_deploy_parts.sh`) : préflight matériel
   (I2C/UART/Bluetooth), paquets système, nginx, environnement virtuel Python
   (`pip install -r requirements.txt`), Gunicorn, variables d'environnement,
   migrations Django + collecte des fichiers statiques, Redis, listeners
   Téléinfo/Bluetooth, permissions, superutilisateur (ignoré s'il existe déjà),
   timer systemd, build et déploiement du frontend React, Certbot/HTTPS, puis une
   vérification finale de tous les services.

Si un module de préflight matériel détecte qu'un redémarrage est nécessaire
(rare après une première installation), le script s'arrête avec un message clair.
Il suffit de redémarrer le Pi (`sudo reboot`) puis de relancer `update.sh` : c'est
idempotent, rien ne sera refait inutilement.

---

## `update_frontend.sh` est obsolète

Ce script existe encore mais ne fait plus que rediriger vers `update.sh` (le
frontend est désormais inclus dans la séquence commune). Utilise directement
`update.sh`.

---

## Vérification

Le script exécute déjà une vérification finale automatique
(`99_verify_deployment.sh`), mais tu peux revérifier manuellement :

```bash
sudo systemctl status nginx gunicorn redis-server teleinfo-listener bluetooth-listener housebrain-periodic.timer --no-pager
```

Tous les services doivent afficher `Active: active (running)`.

### Consulter les logs si problème

```bash
sudo journalctl -u gunicorn -n 50 --no-pager
sudo journalctl -u teleinfo-listener -n 50 --no-pager
sudo journalctl -u bluetooth-listener -n 50 --no-pager
```

### Tester l'accès web

- Frontend : `https://housebrain.emmanuel-oudot.fr/`
- Admin Django : `https://housebrain.emmanuel-oudot.fr/backend/admin/`
- API : `https://housebrain.emmanuel-oudot.fr/api/`

---

## Dépannage

### "Des modifications locales existent dans le repo, update annulé"

Ce Pi ne doit jamais recevoir de modification de code en direct (pas de dev sur le
Pi). Si ce message apparaît, quelque chose a modifié un fichier localement
(édition manuelle, service qui écrit dans un fichier suivi par git...). Inspecte
`git status --porcelain` pour voir quoi, comprends pourquoi avant de trancher, puis
soit committe/pushe ce changement depuis ton poste de dev, soit annule-le sur le Pi
(`git checkout -- <fichier>`) avant de relancer `update.sh`.

### Revenir en arrière après une migration problématique

```bash
sudo systemctl stop gunicorn housebrain-periodic.timer teleinfo-listener bluetooth-listener
cp /home/admin/housebrain/backend/db.sqlite3.pre-update-bak /home/admin/housebrain/backend/db.sqlite3
sudo systemctl start gunicorn housebrain-periodic.timer teleinfo-listener bluetooth-listener
```

Ne fonctionne que pour revenir à l'état d'avant le **dernier** update (une seule
sauvegarde est conservée, pas d'historique).

---

## Documentation complémentaire

- `restart_services.md` - Redémarrage des services
- `see_logs.md` - Consultation des logs

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Juillet 2026
Testé sur : Raspberry Pi 3 B+ - Raspberry Pi OS Lite (64-bit) - Django 5.2
