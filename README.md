# HouseBrain

Système de gestion domotique pour Raspberry Pi.

---

## Fonctionnalités

### Téléinfo (Monitoring électrique)
- Lecture temps-réel compteur Linky (protocole série)
- Composant critique : base de la gestion électrique
- Parsing et validation des trames (checksum)
- Stockage Redis
- Gestion puissance disponible temps-réel

Voir : [docs/features/teleinfo.md](docs/features/teleinfo.md)

### Capteurs Bluetooth
- Détection automatique capteurs BTHome (température, humidité)
- Scanner BLE passif (broadcast, sans appairage)
- Stockage Redis avec détection de tendance
- Affichage par pièce et pilotage chauffage

Voir : [docs/features/bluetooth_sensors.md](docs/features/bluetooth_sensors.md)

### Scheduler
- Orchestrateur de tâches périodiques (systemd timer)
- Exécution toutes les 1 minute
- Tâches indépendantes

Voir : [docs/features/scheduler.md](docs/features/scheduler.md)

### Monitoring énergétique
[Documentation à venir]

### Contrôle chauffage
[Documentation à venir]

### Authentification
- JWT avec cookies HttpOnly
- Access token 15 min, Refresh token 7 jours
- Routes publiques (lecture) / Routes protégées (écriture)

Voir : [docs/features/authentication.md](docs/features/authentication.md)

---

## Architecture

### Backend
- Django 5.2 + Django REST Framework
- SQLite / Redis

### Frontend
- React 19

### Services
- Nginx, Gunicorn
- Teleinfo Listener, Bluetooth Listener
- Scheduler (systemd timer)

---

## Installation

Voir : [docs/software/raspberry_install.md](docs/software/raspberry_install.md)

Déploiement : [docs/software/raspberry_app_deployment.md](docs/software/raspberry_app_deployment.md)

---

## Documentation

### Installation et configuration
- [Installation Raspberry Pi](docs/software/raspberry_install.md)
- [Déploiement application](docs/software/raspberry_app_deployment.md)
- [Configuration HTTPS](docs/software/raspberry_https_setup.md)

### Maintenance
- [Mise à jour](docs/software/raspberry_app_update.md)
- [Redémarrage services](docs/software/restart_services.md)
- [Logs](docs/software/see_logs.md)
- [Désinstallation](docs/software/raspberry_app_remove_full.md)

### Hardware
- [Branchement Téléinfo](docs/hardware/teleinfo_branchement.md)
- [Pilotage chauffage] - Documentation à venir

### Fonctionnalités
- [Téléinfo (Monitoring électrique)](docs/features/teleinfo.md)
- [Capteurs Bluetooth](docs/features/bluetooth_sensors.md)
- [Scheduler](docs/features/scheduler.md)
- [Authentification JWT](docs/features/authentication.md)
- [Monitoring énergétique] - Documentation à venir
- [Contrôle chauffage] - Documentation à venir

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
