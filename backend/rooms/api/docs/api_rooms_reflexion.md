# Documentation API - Endpoint Rooms

## Vue d'ensemble

Cet endpoint retourne la liste des pièces avec leurs informations de chauffage, capteurs de température et radiateurs. Les données sont optimisées pour le frontend avec des transformations pour éviter les calculs côté client.

## Format de réponse

```json
[
  {
    "id": 1,
    "name": "Salon",
    "heating": {
      "mode": "thermostat",
      "value": 21.5
    },
    "temperature": {
      "id": 1,
      "mac_short": "46:C0:F4",
      "signal_strength": 4,
      "measurements": {
        "temperature": 21.79,
        "trend": "same"
      }
    },
    "radiator": {
      "id": 1,
      "state": "on"
    }
  }
]
```

## Transformation des données

### 1. Objet `heating`

Regroupe les informations de pilotage du chauffage de la pièce.

#### Champs source (modèle `Room`)
- `heating_control_mode` : Mode de pilotage ("thermostat" ou "on_off")
- `temperature_setpoint` : Consigne de température (float, en °C)
- `requested_heating_state` : État du chauffage ("off", "on", "unknown")

#### Transformation
```python
heating = {
    "mode": room.heating_control_mode,  # "thermostat" ou "on_off"
    "value": room.temperature_setpoint if room.heating_control_mode == "thermostat"
             else room.requested_heating_state
}
```

#### Exemples
- Mode thermostat : `{"mode": "thermostat", "value": 21.5}`
- Mode on/off : `{"mode": "on_off", "value": "on"}`

---

### 2. Objet `temperature`

Regroupe les informations du capteur de température avec les mesures en temps réel provenant du cache.

#### Champs source
- Modèle `TemperatureSensor` : `id`, `name`, `mac_address`
- Cache `sensors_data` : données temps réel indexées par `mac_address`

#### Structure du cache
```json
{
  "A4:C1:38:46:C0:F4": {
    "mac_address": "A4:C1:38:46:C0:F4",
    "name": "ATC_46C0F4",
    "rssi": -79,
    "measurements": {
      "battery": 18,
      "temperature": 21.79,
      "humidity": 61.27,
      "dt": "2025-10-10T17:33:44.943Z"
    },
    "previous_measurements": {
      "battery": 18,
      "temperature": 21.52,
      "humidity": 61.63,
      "dt": "2025-10-10T17:32:50.060Z"
    }
  }
}
```

#### Transformation

##### `mac_short`
Extrait les 3 derniers segments de l'adresse MAC.

```python
# "A4:C1:38:46:C0:F4" → "46:C0:F4"
mac_short = ":".join(mac_address.split(":")[-3:])
```

##### `signal_strength`
Convertit le RSSI (indicateur de puissance du signal) en nombre de barres (1-5).

| RSSI | Barres | Qualité |
|------|--------|---------|
| ≥ -50 dBm | 5 | Excellent |
| ≥ -60 dBm | 4 | Très bon |
| ≥ -70 dBm | 3 | Bon |
| ≥ -80 dBm | 2 | Moyen |
| < -80 dBm | 1 | Faible |

```python
def rssi_to_bars(rssi):
    if rssi >= -50: return 5
    elif rssi >= -60: return 4
    elif rssi >= -70: return 3
    elif rssi >= -80: return 2
    else: return 1
```

**Note :** 0 barre n'est jamais retourné car cela signifierait l'absence de signal. Dans ce cas, le capteur ne serait pas présent dans le cache ou ses données seraient obsolètes (dt > 5min).

##### `measurements.temperature`
Retourne la température actuelle uniquement si la mesure est récente (< 5 minutes).

```python
from django.utils import timezone
from datetime import timedelta

now = timezone.now()
dt = parse_datetime(cache_data['measurements']['dt'])

if now - dt < timedelta(minutes=5):
    temperature = cache_data['measurements']['temperature']
else:
    temperature = None
```

##### `measurements.trend`
Calcule l'évolution de la température par rapport à la mesure précédente.

**Conditions :**
- Les deux mesures (`measurements` et `previous_measurements`) doivent exister
- L'intervalle entre les deux mesures doit être < 5 minutes
- Sinon, retourne `null`

**Logique :**
```python
if previous_measurements and interval < timedelta(minutes=5):
    temp_current = measurements['temperature']
    temp_previous = previous_measurements['temperature']

    diff = temp_current - temp_previous

    if diff > 0.1:  # Seuil pour considérer une hausse
        trend = "up"
    elif diff < -0.1:  # Seuil pour considérer une baisse
        trend = "down"
    else:
        trend = "same"
else:
    trend = None
```

**Valeurs possibles :**
- `"up"` : Température en hausse
- `"down"` : Température en baisse
- `"same"` : Température stable
- `null` : Données insuffisantes ou obsolètes

#### Cas particuliers

##### Capteur sans données récentes
Si le capteur n'a pas de données dans le cache ou si `dt` > 5 minutes :
```json
"temperature": {
  "id": 1,
  "mac_short": "46:C0:F4",
  "signal_strength": 1,
  "measurements": {
    "temperature": null,
    "trend": null
  }
}
```

##### Room sans capteur
Si `room.temperature_sensor` est `null` :
```json
"temperature": null
```

---

### 3. Objet `radiator`

Représente l'état du radiateur avec une logique qui combine l'état demandé par le système et l'état réel du hardware.

#### Champs source (modèle `Radiator`)
- `id` : Identifiant du radiateur
- `requested_state` : État demandé par le système ("ON", "OFF", "LOAD_SHED")
- `actual_state` : État réel du hardware ("ON", "OFF", "UNDEFINED")
- `last_requested` : Timestamp de la dernière modification de `requested_state`

#### Logique de calcul du `state`

Le champ `state` reflète l'état réel du radiateur en tenant compte des transitions en cours.

| `requested_state` | `actual_state` | `state` retourné | Description |
|-------------------|----------------|------------------|-------------|
| ON | ON | `"on"` | Radiateur allumé et stable |
| OFF | OFF | `"off"` | Radiateur éteint et stable |
| ON | OFF | `"turning_on"` | Radiateur en cours d'allumage |
| OFF | ON | `"shutting_down"` | Radiateur en cours d'extinction |
| LOAD_SHED | ON | `"shutting_down"` | Délestage en cours (extinction) |
| LOAD_SHED | OFF | `"load_shed"` | Délestage actif (radiateur éteint pour réduire la consommation) |
| * | UNDEFINED | `"undefined"` | État matériel indéterminé |

#### États de transition

Les états `"turning_on"` et `"shutting_down"` sont des états transitoires qui apparaissent lorsque le système a demandé un changement d'état mais que le hardware n'a pas encore appliqué la commande.

**Contexte technique :**
- `requested_state` est modifié instantanément par le service de gestion du chauffage ou l'utilisateur
- `actual_state` est mis à jour par une tâche périodique (toutes les ~1 minute) qui applique physiquement les changements
- Durant ce délai, l'état retourné reflète la transition en cours

#### Délestage (Load Shedding)

Le délestage est un mécanisme automatique qui éteint temporairement certains radiateurs pour éviter un dépassement de puissance électrique.

**Pourquoi un état distinct ?**
- `requested_state = "LOAD_SHED"` permet de distinguer une extinction automatique (délestage) d'une extinction manuelle
- Utile pour l'interface utilisateur : afficher un indicateur spécifique pour informer l'utilisateur que le radiateur est éteint temporairement pour raison de gestion d'énergie

**États liés au délestage :**
- `"shutting_down"` : Le système vient de demander un délestage, le radiateur est en cours d'extinction
- `"load_shed"` : Le radiateur est effectivement éteint en délestage

#### Cas particuliers

##### Room sans radiateur
Si `room.radiator` est `null` :
```json
"radiator": null
```

##### État UNDEFINED
Si le hardware n'a pas pu déterminer l'état du radiateur (problème de communication, erreur matérielle) :
```json
"radiator": {
  "id": 1,
  "state": "undefined"
}
```

---

## Implémentation technique

### Sources de données

1. **Base de données Django :**
   - Modèle `Room` : informations de base
   - Modèle `Radiator` : états et configuration
   - Modèle `TemperatureSensor` : référence des capteurs

2. **Cache Django :**
   - Clé `"sensors_data"` : dictionnaire des mesures temps réel
   - Format : `{mac_address: {measurements, previous_measurements, rssi, ...}}`

### Workflow

```
1. Récupérer toutes les Room avec select_related('radiator', 'temperature_sensor')
2. Récupérer cache.get('sensors_data')
3. Pour chaque Room :
   a. Transformer heating (mode + value)
   b. Si temperature_sensor existe :
      - Chercher les données dans le cache par mac_address
      - Calculer mac_short, signal_strength, temperature, trend
   c. Si radiator existe :
      - Calculer state selon la matrice requested/actual
4. Retourner la liste transformée
```

### Performance

- **select_related** : Éviter les N+1 queries pour radiator et temperature_sensor
- **Cache** : Un seul accès au cache pour tous les capteurs
- **Calculs** : Tous effectués côté backend pour alléger le frontend

---

## Exemples complets

### Exemple 1 : Pièce avec thermostat et radiateur allumé
```json
{
  "id": 1,
  "name": "Salon",
  "heating": {
    "mode": "thermostat",
    "value": 21.5
  },
  "temperature": {
    "id": 1,
    "mac_short": "46:C0:F4",
    "signal_strength": 4,
    "measurements": {
      "temperature": 21.79,
      "trend": "up"
    }
  },
  "radiator": {
    "id": 1,
    "state": "on"
  }
}
```

### Exemple 2 : Pièce en mode on/off avec radiateur en délestage
```json
{
  "id": 2,
  "name": "Chambre",
  "heating": {
    "mode": "on_off",
    "value": "on"
  },
  "temperature": {
    "id": 2,
    "mac_short": "B2:1F:44",
    "signal_strength": 3,
    "measurements": {
      "temperature": 22.28,
      "trend": "same"
    }
  },
  "radiator": {
    "id": 2,
    "state": "load_shed"
  }
}
```

### Exemple 3 : Pièce sans capteur de température
```json
{
  "id": 3,
  "name": "Bureau",
  "heating": {
    "mode": "thermostat",
    "value": 20.0
  },
  "temperature": null,
  "radiator": {
    "id": 3,
    "state": "off"
  }
}
```

### Exemple 4 : Pièce avec capteur hors ligne
```json
{
  "id": 4,
  "name": "Garage",
  "heating": {
    "mode": "on_off",
    "value": "off"
  },
  "temperature": {
    "id": 4,
    "mac_short": "4C:64:60",
    "signal_strength": 1,
    "measurements": {
      "temperature": null,
      "trend": null
    }
  },
  "radiator": {
    "id": 4,
    "state": "off"
  }
}
```

---

## Notes d'implémentation

### Gestion des dates

- Utiliser `django.utils.timezone.now()` pour les comparaisons
- Parser les dates ISO du cache avec `dateutil.parser` ou `datetime.fromisoformat()`
- Toujours faire les comparaisons avec des datetimes timezone-aware

### Gestion des erreurs

- Si le cache n'est pas disponible : retourner `temperature: null` pour tous les capteurs
- Si une room référence un capteur qui n'existe pas dans le cache : retourner des valeurs `null` pour les measurements
- Si `actual_state` est `UNDEFINED` : toujours retourner `state: "undefined"` quelle que soit la valeur de `requested_state`

### Seuils configurables

Les valeurs suivantes peuvent être externalisées en configuration :

```python
# settings.py
TEMPERATURE_FRESHNESS_MINUTES = 5  # Durée de validité des mesures
TREND_THRESHOLD_CELSIUS = 0.1      # Seuil de variation pour détecter une tendance
RSSI_THRESHOLDS = [-50, -60, -70, -80]  # Seuils pour signal_strength
```

