# Mise à jour de HouseBrain

Ce guide explique comment mettre à jour votre installation HouseBrain sur Raspberry Pi.

---

## Deux modes de mise à jour

### Option 1 : Mise à jour Backend uniquement
Utilisez cette option si vous n'avez modifié que le code Django (API, listeners, tâches périodiques).

### Option 2 : Mise à jour Backend + Frontend
Utilisez cette option si vous avez modifié le frontend React ou les deux parties.

---

## Procédure de mise à jour

### 1. Connexion SSH

```bash
ssh admin@housebrain
```

---

### 2a. Mise à jour Backend uniquement

```bash
# Rendre le script exécutable (si première fois)
chmod +x /home/admin/housebrain/backend/deployment/scripts/update.sh

# Exécuter la mise à jour backend
/home/admin/housebrain/backend/deployment/scripts/update.sh
```

Le script effectue automatiquement :
1. Arrêt des services (Nginx, Gunicorn, Listeners, Timer)
2. `git pull origin main` (récupération du code)
3. Mise à jour des dépendances Python (`pip install -r requirements.txt`)
4. Application des migrations Django (`python manage.py migrate`)
5. Collecte des fichiers statiques (`python manage.py collectstatic`)
6. Redémarrage de tous les services
7. Vérification des statuts des services

---

### 2b. Mise à jour Backend + Frontend

```bash
# Rendre le script exécutable (si première fois)
chmod +x /home/admin/housebrain/backend/deployment/scripts/update_frontend.sh

# Exécuter la mise à jour complète
/home/admin/housebrain/backend/deployment/scripts/update_frontend.sh
```

Le script effectue automatiquement :
1. Exécution du script `update.sh` (mise à jour backend)
2. Build du frontend React (`npm run build` dans `/home/admin/housebrain/frontend`)
3. Déploiement du build dans `/var/www/housebrain-frontend/`

---

## Vérification

### Vérifier les services

```bash
sudo systemctl status nginx gunicorn teleinfo-listener bluetooth-listener housebrain-periodic.timer --no-pager
```

Tous les services doivent afficher :
```
Active: active (running)
```

### Consulter les logs si problème

```bash
# Gunicorn (Django)
sudo journalctl -u gunicorn -n 50 --no-pager

# Teleinfo Listener
sudo journalctl -u teleinfo-listener -n 50 --no-pager

# Bluetooth Listener
sudo journalctl -u bluetooth-listener -n 50 --no-pager

# Tâches périodiques
sudo journalctl -u housebrain-periodic -n 50 --no-pager
```

### Tester l'accès web

- Frontend : `https://housebrain.emmanuel-oudot.fr/`
- Admin Django : `https://housebrain.emmanuel-oudot.fr/backend/admin/`
- API : `https://housebrain.emmanuel-oudot.fr/api/`

---

## Documentation complémentaire

- `restart_services.md` - Redémarrage des services
- `see_logs.md` - Consultation des logs
- `raspberry_app_remove_full.md` - Désinstallation complète

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
Testé sur : Raspberry Pi 3 B+ - Raspberry Pi OS Lite (64-bit)
