# Capteurs Bluetooth - Température et Humidité

Système de détection et lecture de capteurs Bluetooth utilisant le protocole BTHome.

---

## Vue d'ensemble

Le module Bluetooth détecte automatiquement les capteurs de température et humidité utilisant le protocole BTHome. Les capteurs diffusent leurs mesures via Bluetooth Low Energy (BLE) sans nécessiter de connexion ou d'appairage.

Les données sont stockées en cache Redis uniquement (pas de base de données) car l'historique n'est pas nécessaire pour l'usage actuel.

### Utilisation des mesures

Les mesures de température servent à :
- Afficher la température actuelle par pièce dans l'interface utilisateur
- Piloter intelligemment le chauffage en fonction de la température réelle de chaque pièce

Le contrôle du chauffage basé sur ces mesures est détaillé dans [Contrôle chauffage] - Documentation à venir.

---

## Protocole BTHome

### Principe de fonctionnement

BTHome est un protocole standardisé pour diffuser des mesures via BLE en mode broadcast passif :
- Les capteurs diffusent leurs données en continu
- Aucune connexion requise
- Aucun appairage nécessaire
- Consommation énergétique minimale

Les données sont publiques par nature : pas critique pour des mesures de température domestique et beaucoup plus simple à gérer.

### Format des données

Les mesures sont encodées dans le payload Bluetooth selon le standard BTHome :

**Mesures supportées :**
- Température : `sint16`, facteur 0.01°C
- Humidité : `uint16`, facteur 0.01%
- Batterie : `uint8`, facteur 1%

Documentation complète : https://bthome.io/format/

---

## Architecture

### Service systemd dédié

Le listener fonctionne comme un service systemd indépendant avec watchdog.

**Composants :**
- `bluetooth-listener.service` : Service systemd
- `bluetooth_listener.py` : Scanner BLE asyncio
- `bthome.py` : Décodeur de payload

**Watchdog :**
Le listener notifie systemd à chaque fin de cycle de scan (watchdog 120 secondes).

### Commande Django
```bash
python manage.py run_bluetooth_listener
```

### Cycle de scan

**Timing :**
- 30 secondes de scan actif
- 30 secondes de pause

**Raison :**
La température d'une pièce évolue lentement. Un cycle de 60 secondes permet d'optimiser l'utilisation CPU du Raspberry sans perte d'information utile.

---

## Décodage des mesures

### Flux de traitement

1. **Scan BLE :** Écoute des broadcasts Bluetooth pendant 30s
2. **Détection :** Callback pour chaque paquet BLE reçu
3. **Filtrage :** Sélection des paquets BTHome (service_data)
4. **Décodage :** Parsing binaire du payload BTHome
5. **Buffer :** Accumulation des mesures pendant le scan
6. **Cache :** Mise à jour Redis en fin de cycle

### Parsing binaire

Le payload BTHome est décodé octet par octet :

```python
# Object ID → (nom, type, facteur)
0x01 : ("battery", "uint8", 1)
0x02 : ("temperature", "sint16", 0.01)
0x03 : ("humidity", "uint16", 0.01)
```

Exemple :
```
Payload : [flags][0x02][0x13][0x09]
→ température = 0x0913 (little-endian) * 0.01 = 23.23°C
```

---

## Gestion des données

### Stockage cache uniquement

Les données capteurs sont stockées dans Redis avec :
- Clé : `sensors_data`
- Timeout : `None` (persistant)
- Structure : dictionnaire indexé par adresse MAC

**Pas de base de données :** L'historique des températures n'est pas nécessaire actuellement.

### Structure des données

Pour chaque capteur détecté :

```python
{
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "name": "Sensor Name",
  "rssi": -65,
  "measurements": {
    "temperature": 23.5,
    "humidity": 45.2,
    "battery": 87,
    "dt": "2025-12-27T14:30:00"
  },
  "previous_measurements": {
    "temperature": 23.4,
    "humidity": 45.1,
    "battery": 87,
    "dt": "2025-12-27T14:29:00"
  }
}
```

### Détection de tendance

Deux mesures sont conservées :
- **current** : mesure actuelle (fraîcheur < 1 minute)
- **previous** : mesure précédente (fraîcheur < 2 minutes)

Cela permet de détecter une tendance :
- Température monte
- Température descend
- Température stable

---

## RSSI et qualité du signal

### Conversion RSSI → Barres

Le niveau de signal (RSSI en dBm) est converti en barres (1-5) :

| RSSI | Qualité | Barres |
|------|---------|--------|
| ≥ -50 dBm | Excellent | 5 |
| ≥ -60 dBm | Très bon | 4 |
| ≥ -70 dBm | Bon | 3 |
| ≥ -80 dBm | Moyen | 2 |
| < -80 dBm | Faible | 1 |

---

## Configuration des capteurs

### Prérequis matériel

Les capteurs doivent être flashés avec un firmware compatible BTHome.

Firmware recommandé : https://github.com/pvvx/THB2

Documentation flashage : [À venir - docs/hardware/bluetooth_sensors_flash.md]

### Association capteur → pièce

**Via l'admin Django :**

```
/backend/admin/sensors/temperaturesensor/
```

L'interface admin affiche automatiquement :
- Les capteurs détectés (adresse MAC)
- Leur nom Bluetooth
- Leur niveau de signal RSSI

Sélectionnez un capteur dans la liste déroulante et associez-le à une pièce.

---

## Monitoring

### Page de monitoring
```
/backend/sensors/data/
```

Affiche tous les capteurs détectés avec leurs mesures en temps-réel (JSON).

### API REST
```
/api/sensors/
```

Endpoints REST pour accès programmatique aux données capteurs.

### Logs
```bash
# Logs temps-réel
sudo journalctl -u bluetooth-listener -f

# Dernières erreurs
sudo journalctl -u bluetooth-listener -p err -n 50
```

### Vérifier le service
```bash
# Statut
sudo systemctl status bluetooth-listener

# Redémarrer
sudo systemctl restart bluetooth-listener
```

---

## Dépannage

### Aucun capteur détecté

Vérifier que Bluetooth est actif :
```bash
sudo systemctl status bluetooth
```

Vérifier les logs du listener :
```bash
sudo journalctl -u bluetooth-listener -n 50
```

### Capteur avec signal faible

Si RSSI < -80 dBm :
- Rapprocher le capteur du Raspberry Pi
- Vérifier le niveau de batterie du capteur
- Éviter les obstacles métalliques entre capteur et Raspberry

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
