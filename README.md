# HouseBrain

Système de gestion domotique autonome et léger, optimisé pour Raspberry Pi. HouseBrain propose une solution complète de monitoring énergétique et de communication IoT avec interface web moderne.

## Vue d'ensemble

HouseBrain implémente une architecture microservices complète pour la domotique avec :
- **Monitoring énergétique temps-réel** via protocole Teleinfo (compteurs Linky)
- **Communication Bluetooth** pour capteurs IoT (protocole BTHome)
- **Dashboard web moderne** avec visualisation de données avancée
- **API REST complète** pour intégration externe

## Architecture Technique

### Backend (Django 5.2)
- **6 applications spécialisées** : authentication, consumption, sensors, teleinfo, scheduler
- **Protocoles IoT avancés** : Interface série Teleinfo 1200 bauds + Bluetooth BTHome
- **Algorithmes de traitement** : Interpolation linéaire, validation checksum ASCII, multi-résolution temporelle
- **Services autonomes** : Microservices systemd avec monitoring watchdog

### Frontend (React 19)
- **SPA moderne** avec React Router, visualisation Recharts
- **Dashboard temps-réel** : Graphiques interactifs, jauges de puissance, tableaux de monitoring
- **Design system cohérent** : Dark theme responsive avec micro-animations
- **Architecture modulaire** : Composants réutilisables, service layer robuste

### Stack Technologique
- **Backend** : Django 5.2, Django REST Framework, PostgreSQL/SQLite, Redis
- **Frontend** : React 19, Vite 6, Sass, Recharts
- **Communication** : PySerial (Teleinfo), Bleak (Bluetooth), systemd-python
- **Déploiement** : Nginx, Gunicorn, scripts automatisés, monitoring systemd
- **Tests** : Pytest avec coverage, Freezegun pour tests temporels

## Fonctionnalités Principales

### Monitoring Énergétique
- **Lecture temps-réel** des données compteur Linky via protocole Teleinfo
- **Support multi-tarifs** : Base, HP/HC, EJP, Tempo (bleu/blanc/rouge)
- **Calcul coûts automatique** : Pricing EDF avec évolution tarifaire historique
- **Visualisation multi-résolution** : Données par minute, 30min ou heure
- **Interpolation intelligente** : Reconstruction automatique des données manquantes

### Capteurs IoT Bluetooth
- **Scanner BLE automatique** : Détection capteurs protocole BTHome
- **Multi-capteurs** : Température, humidité, niveau batterie
- **Gestion RSSI** : Monitoring qualité signal et géolocalisation
- **Cache persistant** : Stockage Redis pour données critiques

### Interface Utilisateur
- **Dashboard énergétique** : Graphiques temps-réel avec seuils visuels
- **Navigation intelligente** : Auto-hide, dropdowns animés, responsive mobile-first
- **Visualisation avancée** : RadialBarChart, LineChart, AreaChart avec tooltips interactifs
- **API monitoring** : Endpoints REST pour données Teleinfo et capteurs

## Installation Rapide

### Prérequis
- Raspberry Pi 3B+ ou supérieur
- Compteur Linky avec sortie Teleinfo
- Clé USB pour système
- Connexion WiFi

### Déploiement Automatisé
```bash
# Cloner le projet
git clone https://github.com/manuo1/housebrain.git

# Rendre le script exécutable
chmod +x /home/admin/housebrain/backend/deployment/scripts/deploy.sh

# Lancer le déploiement complet (14 étapes automatisées)
/home/admin/housebrain/backend/deployment/scripts/deploy.sh
```

Le script de déploiement configure automatiquement :
- Système et dépendances
- Services systemd (Gunicorn, Nginx, Redis)
- Listeners Teleinfo et Bluetooth
- Variables d'environnement et base de données
- Monitoring et logging

### Configuration Hardware
Activation du port série pour lecture Teleinfo :
```bash
sudo raspi-config
# 3 Interface Options > I6 Serial Port
# Login shell: No | Hardware enabled: Yes
sudo reboot
```

## Maintenance et Monitoring

### Services Système
```bash
# Statut des services
sudo systemctl status gunicorn nginx teleinfo-listener bluetooth-listener

# Logs temps-réel
sudo journalctl -u teleinfo-listener -f
sudo journalctl -u bluetooth-listener -f
```

### Mise à Jour
```bash
# Backend uniquement
/home/admin/housebrain/backend/deployment/scripts/update.sh

# Backend + Frontend
/home/admin/housebrain/backend/deployment/scripts/update_frontend.sh
```

### Désinstallation
```bash
/home/admin/housebrain/backend/deployment/scripts/remove.sh
```

## Accès Application

Une fois déployé, HouseBrain est accessible via :
- `http://[IP-RASPBERRY]/` - Interface principale
- `http://[IP-RASPBERRY]/teleinfo/` - Monitoring Teleinfo live
- `http://[IP-RASPBERRY]/consumption/` - Historique consommation
- `http://[IP-RASPBERRY]/backend/admin/` - Interface d'administration

## Architecture de Données

### Modèles de Consommation
- **DailyIndexes** : Index énergétiques par minute (1440 points/jour)
- **Multi-résolution** : Agrégation 1min/30min/60min avec downsampling intelligent
- **Calculs différentiels** : Consommation Wh entre index consécutifs
- **Validation données** : Détection anomalies et interpolation sélective

### Gestion Tarifaire
- **Mapping bidirectionnel** : Index énergétique ↔ période tarifaire
- **Pricing dynamique** : Coûts temps-réel avec tarification EDF historique
- **Support multi-options** : Base, HP/HC, EJP, Tempo avec 11 index différents

## Complexité Technique

### Défis Résolus
1. **Protocoles IoT bas niveau** : Parser Teleinfo série + décodeur BTHome binaire
2. **Algorithmes temps-réel** : Interpolation linéaire avec gestion erreurs d'arrondi
3. **Architecture microservices** : Services découplés avec monitoring watchdog
4. **Visualisation complexe** : Dashboard temps-réel avec états loading/error
5. **Déploiement production** : Scripts automatisés avec vérification santé

### Performance et Robustesse
- **Cache multi-niveaux** : Redis persistant + LocMem développement
- **Gestion erreurs** : Retry automatique, fallbacks, validation checksum
- **Monitoring système** : Systemd watchdog, logging structuré, métriques santé
- **Responsive design** : Mobile-first avec breakpoints adaptatifs

## Documentation Complète

La documentation détaillée est disponible dans le dossier `docs/` :
- Guide d'installation Raspberry Pi
- Configuration hardware spécialisée
- Scripts de maintenance et monitoring
- Architecture technique détaillée

## Licence

Ce projet est développé comme système domotique personnel optimisé pour Raspberry Pi.