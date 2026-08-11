# Device — Couche d'abstraction hardware générique

Couche générique de pilotage des devices connectés (aujourd'hui : Shelly), indépendante de tout usage métier. Remplace l'ancien couplage direct Shelly ↔ objet piloté (`actuators.Shelly` + `equipment.PulseSwitch`, retirés).

---

## Vue d'ensemble

Avant cette couche, un objet métier (ex : une porte de garage) référençait directement un `Shelly` avec des méthodes propres à la marque (`set_switch`, `get_input_status`...). Ça mélangeait hardware et métier, et ne s'étendait pas à d'autres marques/capteurs.

`device` isole tout ce qui est propre au matériel : quel modèle de device, comment lui parler (driver), quelles entrées/sorties il expose, et sous quel mode chaque IO est utilisée en ce moment. Au-dessus, les couches métier (`actuators`, `sensors`, `equipment`) composent des objets génériques-mais-typés (`RelayOnOff`, `SensorTrueFalse`) sans jamais connaître le protocole ou l'IP du device.

---

## Modèles

### `Device` / `IPDevice`

Héritage multi-table : `Device` porte le type de modèle (`reference`, généré dynamiquement depuis le registre `DEVICE_MODELS` — pas de `TextChoices` dupliqué) ; `IPDevice(Device)` ajoute `ip` pour les devices connectés en réseau local (aujourd'hui, tous).

### `DeviceIO`

Une ligne par IO physique d'un device (ex : le relais et la borne SW d'un Shelly). Porte une `key` (identifiant technique stable, ex `"relay"`/`"sw"`), un `name` (label lisible, rempli automatiquement depuis la déclaration du modèle), et un `mode` (`IOMode` — `RELAY_ON_OFF` / `SENSOR_TRUE_FALSE` / `NOT_USED_IN_APP`), stocké en DB.

`DeviceIO.get_driver()` résout et renvoie l'instance du driver adapté à ce device.

### `RelayOnOff` / `SensorTrueFalse`

Wrappers OneToOne vers un `DeviceIO`, existant seulement pendant que le mode correspondant est actif sur cette IO (créés/détruits explicitement par le service, jamais par signal Django).

- `RelayOnOff` : `turn_on()`, `turn_off()`, `pulse(seconds)` — délègue au driver.
- `SensorTrueFalse` : `read_state()` — délègue au driver, lève `DeviceDriverError` en cas d'échec de communication (timeout, erreur device...). Ne catch jamais l'erreur elle-même — c'est à l'appelant de décider quoi en faire (afficher, logger, ignorer).

C'est le seul niveau générique/pure-plomberie : aucune interprétation métier (ex : "fermée"/"ouverte") ne vit ici.

---

## Déclaration des modèles de device (`catalog.py`)

Chaque modèle de device supporté est déclaré comme une classe Python typée (`DeviceModelSpec`), listant ses IOs (`IOSpec` : clé, name, `IOType` — capacité déclarative, ex `RELAY_ON_OFF`/`SENSOR_TOGGLEABLE`, non stockée en DB) et sa classe driver (`driver_class`).

`IO_TYPE_ALLOWED_MODES` / `IO_TYPE_DEFAULT_MODE` mappent chaque `IOType` aux `IOMode` DB autorisés/par défaut.

Le registre `DEVICE_MODELS` liste tous les modèles connus (aujourd'hui : `Shelly1MiniGen3`).

---

## Drivers (`drivers/`)

`DeviceDriver` (`base.py`) : interface abstraite commune — `read_io_state(io_key)`, `set_io_output(io_key, ...)`, `set_sensor_mode(io_key, enabled)`. Chaque marque implémente sa propre sous-classe.

`ShellyDriver` : RPC HTTP local, authentification digest SHA-256 (user `"admin"` fixé par le firmware, mot de passe commun stocké dans `.env`). Résout lui-même l'`IPDevice` concret dont il a besoin depuis le `Device` de base reçu — la connaissance de l'IP reste confinée au driver.

Bascule d'une borne entre "suit le relais" (comportement usine, pilotage manuel local possible) et "capteur détaché" (lisible indépendamment, plus de pilotage manuel sur cette borne) : `set_sensor_mode(io_key, enabled)`.

**⚠️ Point de sécurité impératif :** câbler un contact sur une borne avant de l'avoir configurée en capteur détaché peut déclencher le relais au branchement. La configuration logicielle doit toujours précéder le câblage physique.

---

## Service `DeviceIOService`

- `provision_device(device)` : à la création d'un `Device`, crée les `DeviceIO` déclarés par son `DeviceModelSpec` (mode par défaut = état usine, aucun appel driver).
- `set_io_mode(device_io_id, new_mode)` : change le mode d'une IO — verrou (`select_for_update`), validation contre `IO_TYPE_ALLOWED_MODES`, appel driver, suppression de l'ancien wrapper (`RelayOnOff`/`SensorTrueFalse`), création du nouveau, mise à jour du `mode` — le tout `@transaction.atomic` (rollback complet si le driver échoue).

---

## Administration Django

- Création d'un `IPDevice` : provisioning auto (`provision_device()`), auth Shelly activée à la création (`SetAuth`, bloquant si le device n'est pas joignable).
- Changement de mode d'une IO : passe systématiquement par `set_io_mode()` (jamais un save Django direct), avec les choix de mode restreints à ceux valides pour le type réel de l'IO.

---

## Points ouverts / hors scope actuel

- Aucun garde-fou empêchant de changer le mode d'une IO déjà liée à un `Equipment` métier (ex : `GarageDoor`) — à poser si besoin.
- Les `Actuator`/`Sensor` existants pour le chauffage (`actuators.Radiator`, `sensors.TemperatureSensor`) ne sont pas passés par cette couche — ils restent en I2C direct, migration éventuelle non planifiée.

---

Voir aussi : [Équipement porte de garage](equipment_garage_door.md), qui compose cette couche pour un cas métier concret.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
