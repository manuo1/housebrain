# Heating - Contrôle intelligent du chauffage

Algorithmes de contrôle temps-réel du chauffage avec régulation thermostatique et gestion de puissance.

---

## Vue d'ensemble

Le module heating control synchronise les plannings avec les radiateurs en appliquant des algorithmes thermostatiques et en gérant la puissance disponible en temps réel.

---

## Synchronisation globale

Le scheduler exécute 3 fonctions dans l'ordre toutes les 1 minute :

**1. Synchronisation plannings → Rooms**
```python
synchronize_room_requested_heating_states_with_room_heating_day_plan()
```
Lit les plannings du jour et met à jour `requested_heating_state` de chaque Room.

**2. Synchronisation Rooms → Radiators (2 fonctions distinctes, pour rendre explicite ce qui a un effet hardware immédiat)**
```python
radiators_to_update = resolve_radiators_to_update()
turn_off_radiators_and_apply_to_hardware(radiators_to_update)
queue_radiators_to_turn_on(radiators_to_update)
```
`resolve_radiators_to_update()` calcule qui doit changer (`get_radiators_to_update`). `turn_off_radiators_and_apply_to_hardware()` écrit `requested_state = OFF` pour les radiateurs à éteindre **et** applique immédiatement au hardware (`RadiatorSyncService.synchronize_database_and_hardware()`, qui resynchronise toute la flotte d'un coup — impossible de la cibler sur un sous-ensemble, lecture/écriture I2C batchée). `queue_radiators_to_turn_on()` ne touche ni `requested_state` ni le hardware — elle place juste les radiateurs à allumer dans le cache.

**3. Application hardware pour l'allumage (via listener Teleinfo)**
```python
remaining_power = get_instant_remaining_power()
ensure_power_not_exceeded(remaining_power)
turn_on_radiators_according_to_the_available_power(remaining_power)
```
`get_instant_remaining_power()` (dans `teleinfo/services.py`) calcule une seule fois la puissance disponible moins la marge de sécurité, et c'est cette valeur qui circule en paramètre — évite que plusieurs fonctions (allumage radiateurs, futur allumage chauffe-eau, délestage) lisent chacune la puissance dispo indépendamment et s'allouent la même puissance sans se coordonner.

---

## Étape 1 : Plannings → Rooms

### Flux de traitement

Pour chaque pièce ayant un planning défini pour le jour :

1. **Lecture du créneau actuel**
   - Récupération des slots du `SchedulePattern` (app `planning`)
   - Recherche du slot correspondant à l'heure actuelle

2. **Traitement selon le type de slot**

**Si TEMPERATURE :**
- Mode : THERMOSTAT
- `temperature_setpoint` = valeur du slot
- `requested_heating_state` = calculé par algorithme thermostat

**Si ONOFF :**
- Mode : ONOFF
- `temperature_setpoint` = null
- `requested_heating_state` = valeur du slot ("on" → ON, "off" → OFF)

**Si aucun créneau (période non définie) :**
- Mode : ONOFF
- `temperature_setpoint` = null
- `requested_heating_state` = OFF

3. **Mise à jour Room**
   - Si changement détecté → update en base

---

## Algorithme thermostat

### Principe

Régulation avec hystérésis et anticipation par tendance de température.

### Hystérésis

**Constante :** `HYSTERESIS = 0.5°C`

**Zones de décision :**

```
température_actuelle >= consigne + 0.5°C  →  OFF (bien au-dessus)
consigne - 0.5°C < température_actuelle < consigne + 0.5°C  →  Zone d'hystérésis (utilise tendance)
température_actuelle <= consigne - 0.5°C  →  ON (bien en-dessous)
```

### Utilisation de la tendance

Dans la zone d'hystérésis, la décision est prise selon la tendance (up/down/same) :

**Si température > consigne :**
- Tendance UP → OFF (continue de monter)
- Tendance DOWN → ON (risque de repasser sous consigne)
- Tendance SAME → OFF (stable au-dessus)

**Si température ≤ consigne :**
- Tendance UP → OFF (va atteindre consigne)
- Tendance DOWN → ON (continue de descendre)
- Tendance SAME → ON (stable en-dessous)

### Gestion des données manquantes

**Si température actuelle manquante mais température précédente disponible :**
- Utilise température précédente comme température actuelle
- Continue le calcul normalement

**Si aucune donnée température :**
- Conserve `requested_heating_state` précédent de la Room

### Exemple de fonctionnement

**Consigne :** 19.5°C

```
Température actuelle : 18.8°C
→ 18.8 <= 19.0 (consigne - hystérésis)
→ ON (bien en-dessous)

Température actuelle : 19.3°C, tendance DOWN
→ Dans zone hystérésis, température ≤ consigne, tendance DOWN
→ ON (risque de continuer à descendre)

Température actuelle : 19.7°C, tendance UP
→ Dans zone hystérésis, température > consigne, tendance UP
→ OFF (continue de monter)

Température actuelle : 20.2°C
→ 20.2 >= 20.0 (consigne + hystérésis)
→ OFF (bien au-dessus)
```

---

## Étape 2 : Rooms → Radiators

### Flux de traitement

1. **Récupération des états**
   - Lecture `requested_heating_state` de chaque Room
   - Lecture `requested_state` du Radiator associé

2. **Détection des changements**

Radiator nécessite mise à jour si :
```python
radiator.requested_state != room.requested_heating_state
```

**Mapping :**
- Room ON → Radiator doit être ON
- Room OFF → Radiator doit être OFF ou LOAD_SHED

3. **Séparation selon action**

**Radiateurs à éteindre** (`turn_off_radiators_and_apply_to_hardware()`) :
- `requested_state` mis à `OFF` directement en base (`set_radiators_requested_state_to_off()`) — aucun problème à éteindre sans vérifier la puissance
- Appliqué immédiatement au hardware dans la même fonction (`RadiatorSyncService.synchronize_database_and_hardware()`)

**Radiateurs à allumer** (`queue_radiators_to_turn_on()`) :
- `requested_state` n'est PAS modifié ici, aucun appel hardware — stockage dans le cache Redis (liste triée par importance), délégation au listener Teleinfo qui est le seul à connaître la puissance disponible en temps réel avant de décider d'un allumage

---

## Étape 3 : Allumage selon puissance

### Cache des radiateurs en attente

**Clé Redis :** `radiators_to_turn_on`

**Structure :**
```python
[
  {"id": 1, "power": 2000, "importance": 0},
  {"id": 2, "power": 1500, "importance": 2}
]
```

### Algorithme d'allumage

**Appelé par le listener Teleinfo à chaque trame complète :**

1. **Récupération des radiateurs en attente**
   ```python
   radiators = get_radiators_to_turn_on_in_cache()
   ```

2. **Tri par priorité**
   ```python
   sorted_radiators = sorted(radiators, key=lambda x: (x["importance"], -x["power"]))
   ```
   - CRITICAL (0) en premier, puis HIGH (1), MEDIUM (2), LOW (3)
   - À importance égale, puissance décroissante

3. **Puissance disponible**
   ```python
   # calculée une fois par le listener (teleinfo.services.get_instant_remaining_power),
   # marge de sécurité déjà retranchée, passée en paramètre
   ```

4. **Sélection des radiateurs**
   - Parcours séquentiel de la liste triée
   - Ajout si puissance suffisante
   - Arrêt si puissance insuffisante

5. **Application**
   - Allumage : `set_radiators_requested_state_to_on(can_turn_on)`
   - Délestage : `apply_load_shedding_to_radiators(cannot_turn_on)`
   - Mise à jour cache : conservation des radiateurs non allumés

---

## Mappers

### Room ↔ Radiator

**Fonction :** `radiator_state_matches_room_state()`

Vérifie si l'état du radiateur correspond à l'intention de la pièce :

| room.requested_heating_state | radiator.requested_state | Match |
|------------------------------|--------------------------|-------|
| ON | ON | True |
| ON | OFF | False |
| ON | LOAD_SHED | False |
| OFF | OFF | True |
| OFF | LOAD_SHED | True |
| UNKNOWN | * | False |

### Slot → Room state

**Fonction :** `heating_pattern_slot_value_to_room_requested_heating_state()`

Conversion valeur slot ONOFF vers état Room :

| Valeur slot | requested_heating_state |
|-------------|-------------------------|
| "on" | ON |
| "off" | OFF |
| autre | UNKNOWN |

---

## Gestion des erreurs

### Température indisponible

Si aucune donnée température pour une pièce en mode thermostat :
- Conservation de `requested_heating_state` précédent
- Pas de changement d'état

### Planning absent

Si aucun planning défini pour un jour :
- Pas de mise à jour de la Room
- `requested_heating_state` reste inchangé

### Puissance insuffisante

Radiateurs ne pouvant pas être allumés :
- État : LOAD_SHED
- Conservation dans cache pour tentative ultérieure

---

## Logs et monitoring

### Identification des logs

```bash
# Synchronisation plannings
sudo journalctl -u housebrain-periodic | grep "heating_synchronization"

# Thermostat
sudo journalctl -u housebrain-periodic | grep "thermostat"

# Allumage radiateurs
sudo journalctl -u teleinfo-listener | grep "turn_on_radiators"
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
