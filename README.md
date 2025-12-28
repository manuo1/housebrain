# HouseBrain

Système de gestion domotique pour Raspberry Pi avec monitoring énergétique et contrôle de chauffage.

---

## Fonctionnalités

### Monitoring électrique temps-réel
Visualisation en direct des données du compteur Linky (Téléinfo).
[Documentation à venir]

### Analyse de consommation
Historique et graphiques de consommation électrique avec calcul des coûts.
[Documentation à venir]

### Planification du chauffage
Éditeur de plannings horaires par pièce avec duplication facilitée.
[Documentation à venir]

### Contrôle des radiateurs
Pilotage intelligent des radiateurs avec régulation thermostatique.
[Documentation à venir]

### Dashboard pièces
Vue d'ensemble température et état chauffage par pièce.
[Documentation à venir]

---

## Architecture

### Backend
- Django 5.2 + Django REST Framework
- SQLite / Redis
- Services systemd : Gunicorn, Teleinfo Listener, Bluetooth Listener, Scheduler

### Frontend
- React 19 + Vite 6
- Graphiques custom (CSS/HTML)
- Authentification JWT

### Stack
- Nginx
- PySerial (Téléinfo), Bleak (Bluetooth)
- MCP23017 (I2C), GPIO

---

## Installation

Voir la documentation complète : [docs/software/raspberry_install.md](docs/software/raspberry_install.md)

Pour le déploiement : [docs/software/raspberry_app_deployment.md](docs/software/raspberry_app_deployment.md)

---

## Documentation

### Installation et configuration
- [Installation initiale du Raspberry Pi](docs/software/raspberry_install.md)
- [Déploiement de l'application](docs/software/raspberry_app_deployment.md)
- [Configuration HTTPS](docs/software/raspberry_https_setup.md)

### Maintenance
- [Mise à jour](docs/software/raspberry_app_update.md)
- [Redémarrage des services](docs/software/restart_services.md)
- [Consultation des logs](docs/software/see_logs.md)
- [Désinstallation](docs/software/raspberry_app_remove_full.md)

### Hardware
- [Branchement Téléinfo](docs/hardware/teleinfo_branchement.md)
- Pilotage chauffage MCP23017 - Documentation à venir

### Architecture technique

**Backend :**
- [Téléinfo - Lecture compteur](docs/backend/teleinfo.md)
- [Pilotage radiateurs](docs/backend/radiator_control.md)
- [Planification chauffage](docs/backend/heating_planning.md)
- [Contrôle chauffage](docs/backend/heating_control.md)
- [Gestion des pièces](docs/backend/rooms.md)
- [Monitoring consommation](docs/backend/energy_consumption.md)
- [Monitoring système](docs/backend/monitoring.md)
- [Capteurs Bluetooth](docs/backend/bluetooth_sensors.md)
- [Scheduler](docs/backend/scheduler.md)
- [Authentification JWT - Backend](docs/backend/authentication.md)

**Frontend :**
- [Authentification JWT - Frontend](docs/frontend/authentication.md)
- [Live Téléinfo](docs/frontend/live_teleinfo.md)
- Documentation autres pages à venir

---

## Services

| Service | Description |
|---------|-------------|
| nginx | Serveur web |
| gunicorn | Application Django |
| redis-server | Cache |
| teleinfo-listener | Lecture Linky |
| bluetooth-listener | Communication BLE |
| housebrain-periodic.timer | Tâches périodiques |

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
