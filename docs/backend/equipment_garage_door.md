# Équipement — Porte de garage

Couche métier au-dessus de [Device](device.md) pour la porte de garage : moteur à impulsion + capteur de position, agrégés en un équipement affichable/pilotable côté front.

Remplace l'ancien `equipment.PulseSwitch` (retiré) — le pilotage passait auparavant par un `Shelly` directement, sans capteur de retour.

---

## Vue d'ensemble

Trois couches :

1. **`device`** (voir sa doc dédiée) : plomberie hardware pure, un `RelayOnOff` et un `SensorTrueFalse` génériques.
2. **`actuators`/`sensors`** : wrappers génériques-mais-avec-sens-métier, un cran au-dessus de la plomberie pure.
3. **`equipment`** : composition + contrat commun pour l'affichage/le pilotage côté front.

---

## `actuators.SingleButtonMotor`

Moteur piloté comme un bouton-poussoir unique (ex : moteur de porte de garage câblé sur un relais Shelly) : chaque `trigger()` est une pression momentanée. Le cycle interne du moteur (ex : ouvre → stop → ferme → stop) décide de l'effet réel — non déductible côté logiciel, donc ce modèle ne garde aucun état ni sens.

```python
relay_on_off    # OneToOne vers device.RelayOnOff
name            # unique
pulse_seconds   # durée du pulse, configurable par instance

trigger()       # relay_on_off.pulse(pulse_seconds)
```

Pas de verrou anti-concurrence ni de debounce : aucun risque matériel identifié (contrairement à un bus I2C partagé — chaque appel HTTP Shelly est indépendant), et le long-press prévu côté front couvre déjà le risque réel (déclenchement accidentel).

---

## `sensors.DoorContactSensor`

Capteur de contact magnétique (reed switch) rapportant si une porte est fermée.

```python
sensor_true_false   # OneToOne vers device.SensorTrueFalse
name                # unique
closed_when_true    # bool — la porte est fermée quand l'état brut lu est vrai (décoché si c'est l'inverse)

is_closed() -> bool
get_readable_state() -> str   # "Porte fermée" / "Porte ouverte"
```

`closed_when_true` absorbe la polarité réelle du câblage (nom choisi pour porter la règle de lecture directement, plutôt qu'un champ générique type `inverted` qui obligerait à connaître une convention externe implicite).

Les deux méthodes ne catchent pas `DeviceDriverError` — elles la laissent remonter telle quelle. Chaque couche reste pure plomberie ; décider quoi faire d'un échec de lecture (afficher, logger, retry) appartient à l'appelant.

---

## `equipment.Equipment` (abstrait)

Base commune à tout équipement affichable en card sur la home : seul `get_readable_state() -> str` est garanti. Volontairement minimal — un futur équipement à deux capteurs (ex : volet avec fins de course haut/bas) peut combiner plusieurs sources en interne sans que ce contrat change.

### `equipment.SingleButtonEquipment(Equipment)` (abstrait)

Ajoute `trigger() -> None`, réservé aux équipements à action unique. Un futur volet roulant (`up()`/`down()` séparés) hériterait d'`Equipment` directement, pas de cette classe.

### `equipment.GarageDoor(SingleButtonEquipment)`

```python
interaction_type = "long_press_with_state"   # attribut de classe, lu par le registre/l'API

name
motor                  # OneToOne vers actuators.SingleButtonMotor, on_delete=PROTECT
door_sensor             # OneToOne vers sensors.DoorContactSensor, on_delete=PROTECT
select_related_fields    # chemins FK à précharger (perf, voir API)

trigger()               # délègue à motor.trigger()
get_readable_state()     # délègue à door_sensor.get_readable_state()
```

`on_delete=PROTECT` sur les deux FK : empêche de supprimer le moteur ou le capteur tant que la porte existe.

---

## Registre (`equipment/registry.py`)

```python
EQUIPMENT_MODELS = [GarageDoor]  # futur : + RollerShutter, Light...
EQUIPMENT_MODELS_BY_NAME = {model_name: model_class, ...}
```

Même esprit que `device.catalog.DEVICE_MODELS`. Ajouter un futur type d'équipement = l'ajouter ici, sans toucher au code générique (selectors/vues).

**Id composite** : `"<model_name>:<pk>"` (ex : `"garagedoor:1"`) — chaque type ayant sa propre table/PK, un id brut serait ambigu dès qu'un deuxième type existe.

---

## API REST

```
GET  /api/equipment/                    # Public
POST /api/equipment/<id>/trigger/       # Authentifié
```

### `GET /api/equipment/`

```json
{
  "long_press_with_state": [
    {"id": "garagedoor:1", "name": "Porte de garage", "state": "Porte fermée", "operational": true}
  ]
}
```

Groupé par `interaction_type` (un groupe par pattern d'interaction front). Le selector interroge chaque modèle du registre correspondant, avec `select_related(*model.select_related_fields)` pour ramener toute la chaîne de FK (`door_sensor__sensor_true_false__device_io__device`, `motor__relay_on_off__device_io__device`) en une seule requête SQL, peu importe le nombre d'équipements — évite le N+1.

Si `DeviceDriverError` à la lecture d'un équipement précis (device injoignable) : cet équipement passe en `state: null, operational: false`, le reste de la liste répond normalement (pas d'échec global).

### `POST /api/equipment/<id>/trigger/`

| Code | Cas |
|------|-----|
| 204 | Déclenché avec succès |
| 400 | Équipement trouvé mais pas un `SingleButtonEquipment` |
| 404 | `model_name` inconnu du registre, ou `pk` introuvable |
| 503 | `DeviceDriverError` (device injoignable pendant le trigger) |

Permissions par défaut du projet (`IsAuthenticatedOrReadOnly`) — pas de gestion custom.

---

## Administration Django

**`SingleButtonMotorAdmin`** : action "Déclencher" en masse, catch `DeviceDriverError` par item.

**`DoorContactSensorAdmin`** : colonne "État" en lecture seule, lit en direct (`"Erreur : ..."` si échec).

**`GarageDoorAdmin`** : combine les deux — colonne état live + action "Déclencher".

---

## Frontend

🚧 **Pas commencé.** Prochaine étape du chantier.

Idées déjà posées (pas encore implémentées) :
- Cards sur la home, une par équipement (`long_press_with_state` → long-press avec décompte visuel).
- Polling de l'état uniquement pendant que l'écran d'équipements est affiché (pas de polling permanent en arrière-plan).

**Point non résolu identifié :** avec du polling seul, un trigger juste après un cycle de polling ne sera visible qu'au polling suivant (le bouton peut sembler n'avoir rien fait) — et lire l'état immédiatement après le trigger ne marche pas non plus (~1s de délai mécanique avant que la porte bouge réellement). "Fermée" reste le seul état certain via le capteur. Solution à trouver au moment du chantier front.

---

## Nettoyage legacy (fait)

L'ancien `actuators.Shelly` + `actuators/drivers/shelly.py` (remplacés par `device.IPDevice` + `device/drivers/shelly.py`) et l'ancien `equipment.PulseSwitch` (service, API, tests) ont été retirés. Migrations squashées proprement (pas de perte de données sur `Radiator`), procédure de migration Pi (arrêt service → migrate sur l'ancien code → deploy → migrate no-op → restart) validée en prod.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
