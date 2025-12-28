# Rooms - Gestion des pièces

Module d'agrégation et de gestion des pièces avec leur configuration de chauffage.

---

## Vue d'ensemble

Le module Rooms constitue la couche d'abstraction centrale qui relie les capteurs de température, les radiateurs et la configuration de chauffage par pièce. Il fournit une API REST unifiée pour le frontend.

---

## Modèle Room

### Champs principaux

```python
name                      # Nom de la pièce
temperature_sensor        # FK vers TemperatureSensor (nullable)
radiator                  # FK vers Radiator (nullable)
heating_control_mode      # Mode de pilotage (THERMOSTAT ou ONOFF)
temperature_setpoint      # Consigne de température en °C (nullable)
requested_heating_state   # État demandé final (ON/OFF/UNKNOWN)
```

### Modes de pilotage

**THERMOSTAT : Piloté par plannings de température**
- La pièce suit une consigne de température variable selon les plannings
- Le système calcule automatiquement si le chauffage doit être allumé ou éteint
- `temperature_setpoint` contient la consigne actuelle
- `requested_heating_state` est mis à jour par l'algorithme thermostatique

**ONOFF : Piloté par plannings on/off**
- La pièce suit un planning d'états on/off directs
- Pas de régulation par température
- `temperature_setpoint` n'est pas utilisé
- `requested_heating_state` est copié directement depuis le planning

---

## État demandé final (requested_heating_state)

### Principe fondamental

**IMPORTANT :** `requested_heating_state` est toujours utilisé quel que soit le mode de pilotage. Il contient l'état final demandé pour le chauffage de la pièce.

### Flux selon le mode

**Mode ONOFF :**
```
Planning horaire → requested_heating_state (ON/OFF)
```

**Mode THERMOSTAT :**
```
Planning température → temperature_setpoint
↓
Algorithme thermostatique compare (température mesurée vs consigne)
↓
requested_heating_state (ON/OFF)
```

### Synchronisation avec les radiateurs

Quel que soit le mode, `requested_heating_state` est ensuite appliqué au radiateur associé :

```
requested_heating_state → radiator.requested_state
```

Le service de synchronisation (module heating) s'occupe de cette propagation.

Voir : [Contrôle chauffage] - Documentation à venir

---

## API REST

### Endpoint principal

```
GET /api/rooms/
```

Retourne la liste de toutes les pièces avec leurs données temps-réel agrégées.

### Structure de réponse

```json
{
  "id": 1,
  "name": "Salon",
  "heating": {
    "mode": "thermostat",
    "value": "19.5"
  },
  "temperature": {
    "id": 3,
    "mac_short": "46:C0:F4",
    "signal_strength": 4,
    "measurements": {
      "temperature": 19.2,
      "trend": "up"
    }
  },
  "radiator": {
    "id": 2,
    "state": "on"
  }
}
```

### Champs de réponse

**heating :**
- `mode` : "thermostat" ou "on_off"
- `value` : Consigne température (mode thermostat) ou état (mode on_off)

**temperature :**
- `id` : ID du capteur
- `mac_short` : 3 derniers segments de l'adresse MAC (ex: "46:C0:F4")
- `signal_strength` : Qualité du signal en barres (1-5)
- `measurements.temperature` : Température actuelle en °C (null si données périmées > 2 min)
- `measurements.trend` : Tendance ("up", "down", "same", null)

**radiator :**
- `id` : ID du radiateur
- `state` : État calculé (voir section États calculés)

---

## États calculés du radiateur

L'état du radiateur est calculé en combinant `requested_state` et `actual_state` :

| requested_state | actual_state | État API |
|-----------------|--------------|----------|
| ON | ON | `on` |
| ON | OFF | `turning_on` |
| OFF | OFF | `off` |
| OFF | ON | `shutting_down` |
| LOAD_SHED | OFF | `load_shed` |
| LOAD_SHED | ON | `shutting_down` |
| * | UNDEFINED | `undefined` |

**États transitoires :**
- `turning_on` : Le radiateur a été demandé ON mais n'est pas encore physiquement allumé
- `shutting_down` : Le radiateur a été demandé OFF mais n'est pas encore physiquement éteint

Ces états transitoires disparaissent après la prochaine synchronisation hardware (max 1 minute).

---

## Agrégation des données

### Source des données

L'API `/api/rooms/` agrège les données de plusieurs sources :

**Base de données :**
- Configuration de la pièce (Room)
- État demandé et mode de pilotage
- Associations radiateur et capteur

**Cache Redis :**
- Mesures temps-réel des capteurs Bluetooth
- RSSI (signal strength)
- Timestamps des mesures

### Enrichissement temps-réel

Pour chaque pièce :

1. **Récupération BDD :** Configuration + associations FK
2. **Enrichissement cache :** Ajout des mesures Bluetooth du capteur associé
3. **Calcul :**
   - Tendance température (current vs previous)
   - État radiateur (requested vs actual)
   - Signal strength (conversion RSSI → barres)
4. **Transformation :** Format API unifié

---

## Administration Django

### Interface admin

```
/backend/admin/rooms/room/
```

**Champs configurables :**
- Nom de la pièce
- Association capteur de température
- Association radiateur
- Mode de pilotage (thermostat / on_off)
- Consigne de température
- État demandé du chauffage

**Actions en masse :**
- Allumer le chauffage des pièces sélectionnées
- Éteindre le chauffage des pièces sélectionnées

Ces actions mettent à jour `requested_heating_state` et déclenchent immédiatement la synchronisation avec les radiateurs.

---

## Gestion des données manquantes

### Capteur non associé

Si `temperature_sensor` est null, l'API retourne :
```json
"temperature": null
```

### Radiateur non associé

Si `radiator` est null, l'API retourne :
```json
"radiator": null
```

### Mesures périmées

Si les données du capteur datent de plus de 2 minutes :
```json
"temperature": {
  "measurements": {
    "temperature": null,
    "trend": null
  }
}
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
