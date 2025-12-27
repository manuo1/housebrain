# HouseBrain

Système de gestion domotique pour Raspberry Pi.

---

## Fonctionnalités

### Scheduler
- Orchestrateur de tâches périodiques (systemd timer)
- Exécution toutes les 1 minute
- Tâches indépendantes

Voir : [docs/features/scheduler.md](docs/features/scheduler.md)

### Monitoring énergétique
[Documentation à venir]

### Capteurs Bluetooth
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
- [Scheduler](docs/features/scheduler.md)
- [Authentification JWT](docs/features/authentication.md)
- [Monitoring énergétique] - Documentation à venir
- [Contrôle chauffage] - Documentation à venir
- [Capteurs Bluetooth] - Documentation à venir

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
