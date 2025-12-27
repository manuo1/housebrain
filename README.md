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

### Pilotage radiateurs (Fil pilote)
- Contrôle radiateurs électriques via MCP23017 (I2C)
- Architecture découplée software/hardware
- Délestage intelligent par ordre d'importance
- Synchronisation centralisée (scheduler + listener Teleinfo)

Voir : [docs/features/radiator_control.md](docs/features/radiator_control.md)

### Monitoring système
- Collecte automatique logs journalctl (6 services)
- Filtrage intelligent par keywords
- Consultation centralisée via admin Django

Voir : [docs/features/monitoring.md](docs/features/monitoring.md)

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
- Historisation index Linky minute par minute (1440 points/jour)
- Multi-résolution (1 min, 30 min, 60 min)
- Interpolation linéaire des données manquantes
- Calcul coûts avec pricing EDF historique
- API REST avec totaux par période tarifaire

Voir : [docs/features/energy_consumption.md](docs/features/energy_consumption.md)

### Contrôle chauffage
- Gestion des pièces (Rooms) : agrégation radiateur + capteur + config
- 2 modes de pilotage : THERMOSTAT (consigne température) ou ONOFF (planning direct)
- État demandé final (`requested_heating_state`) calculé selon le mode
- API REST temps-réel avec données agrégées et états calculés

Voir : [docs/features/rooms.md](docs/features/rooms.md)

[Algorithmes thermostat et plannings] - Documentation à venir

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
- [Pilotage radiateurs](docs/features/radiator_control.md)
- [Monitoring consommation](docs/features/energy_consumption.md)
- [Monitoring système](docs/features/monitoring.md)
- [Capteurs Bluetooth](docs/features/bluetooth_sensors.md)
- [Gestion des pièces](docs/features/rooms.md)
- [Scheduler](docs/features/scheduler.md)
- [Authentification JWT](docs/features/authentication.md)

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
