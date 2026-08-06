# Equipment - Interrupteurs à impulsion (PulseSwitch / Shelly)

Module de pilotage d'équipements à commande impulsionnelle (porte de garage, futur portail) via des relais Shelly.

---

## Vue d'ensemble

L'app `equipment` regroupe les objets pilotés qui n'ont pas de notion de pièce (pas de FK vers `Room`), contrairement aux radiateurs. Elle vit au même niveau métier que `rooms`, au-dessus de la couche hardware `actuators`.

Premier objet du module : `PulseSwitch`, pour tout équipement qui ne nécessite qu'une impulsion pour agir — l'appareil lui-même gère ensuite le mouvement (ex : moteur de porte de garage). Ce n'est pas un modèle pour du on/off permanent (ex : une lampe), qui aura son propre modèle plus tard.

**Différence structurelle avec les radiateurs :** pas de pattern `requested_state` / `actual_state` synchronisé périodiquement. Une impulsion se déclenche et s'exécute en synchrone dans la requête HTTP — une latence d'1 minute (cycle du scheduler) serait inacceptable pour une porte.

---

## Modèle Shelly (app actuators)

Représente un relais Shelly physique, indépendant de l'objet métier qu'il pilote.

```python
name        # Nom du Shelly
reference   # Référence exacte (TextChoices) — détermine le comportement du driver
ip          # Adresse IPv4 locale, unique
```

**Référence supportée aujourd'hui :** `SHELLY_1_MINI_GEN3` uniquement. Le driver suppose un device mono-relais (`SWITCH_ID = 0`, `INPUT_ID = 0`) — ajouter une référence multi-relais nécessiterait des changements de code (id de switch paramétrable), pas juste une entrée de choix supplémentaire.

**Association à un objet métier :** simple FK objet → Shelly (`PulseSwitch.shelly`). Un Shelly ne pilote qu'un seul objet à la fois ; aucun cas d'usage identifié pour plusieurs Shelly sur un même objet.

---

## Driver ShellyDriver (actuators/drivers/shelly.py)

Communication RPC HTTP locale (pas de HTTPS — jugé inutile sur un LAN de confiance), authentification digest SHA-256.

### Authentification

- User toujours `"admin"` — fixé par le firmware Shelly, non configurable (confirmé par erreur device -103 si un autre user est tenté).
- Mot de passe commun à tous les Shelly, stocké dans `.env` (`SHELLY_AUTH_PASSWORD`), pas saisi par device.
- Provisioning automatique à la création d'un Shelly dans l'admin (`ShellyAdminForm.clean()`) : appel `Shelly.SetAuth`, bloquant si le device n'est pas joignable ou refuse (401 → message actionnable invitant à vérifier le mot de passe ou factory-reset le device).
- Une édition ultérieure (renommage, etc.) ne redéclenche pas le provisioning — le device n'a pas besoin d'être en ligne pour ça.

### Méthodes principales

```python
set_switch(on, toggle_after=None)   # Switch.Set — toggle_after déclenche une impulsion (auto-retour à l'état opposé après N secondes, pas de rappel nécessaire)
get_switch_status()                  # Switch.GetStatus — état du relais
get_input_status()                   # Input.GetStatus — état de la borne SW (si quelque chose y est câblé)
get_device_info()                    # Shelly.GetDeviceInfo — identité/statut auth du device
set_auth(password)                   # Shelly.SetAuth — active l'auth digest
set_sw_terminal_as_sensor()          # Reconfigure la borne SW en entrée détachée du relais
set_sw_terminal_as_switch()          # Restaure la borne SW comme interrupteur du relais (comportement usine)
```

### Borne SW : capteur ou interrupteur

Par défaut (comportement usine), la borne **SW** du Shelly pilote directement le relais : un bouton câblé dessus permet d'actionner la sortie localement, en plus du pilotage à distance.

Pour câbler un capteur de position (ex : reed switch magnétique sur la porte de garage) sans qu'il déclenche le relais, la borne doit être détachée :

- **`set_sw_terminal_as_sensor()`** : `Switch.SetConfig(in_mode="detached", initial_state="off")` + `Input.SetConfig(type="switch")`. La borne SW devient une entrée lisible via `get_input_status()`, sans effet sur le relais. `initial_state="off"` garantit qu'après un reboot/coupure, le relais reste éteint plutôt que de tenter de restaurer un état transitoire.
- **`set_sw_terminal_as_switch()`** : opération inverse — `in_mode="follow", initial_state="match_input"` (combinaison usine). La borne SW repilote directement le relais.

**⚠️ Point de sécurité impératif :** câbler un contact sur SW *avant* d'avoir appliqué `set_sw_terminal_as_sensor()` peut déclencher le relais au branchement (ouverture intempestive de la porte, tant que le mode reste `follow`). La configuration doit toujours précéder le câblage.

Ces deux méthodes sont exposées comme **actions admin** sur `ShellyAdmin` (sélection d'un ou plusieurs Shelly dans la liste). Idempotentes côté device — rejouables sans risque.

### Gestion d'erreur

Toute erreur (timeout, HTTP, RPC) lève `ShellyError` avec message explicite. Le cas 401 a un message dédié orientant vers la vérification du mot de passe ou un factory-reset physique (appui 10s sur le bouton du device).

---

## Modèle PulseSwitch (app equipment)

```python
name                # Nom, unique
shelly               # FK vers Shelly (nullable) — SET_NULL si le Shelly est supprimé
status                # IDLE / IN_PROGRESS — verrou applicatif
last_triggered_at    # Timestamp du dernier déclenchement réussi
```

Pas de FK vers `Room` : une porte de garage, un chauffe-eau ou une pompe de piscine n'ont pas de notion de pièce.

---

## Service PulseSwitchService

### Exécution synchrone

`PulseSwitchService.trigger(pulse_switch_id)` attend la fin de l'appel RPC Shelly avant de retourner — pas de tâche périodique, pas d'état à réconcilier (le Shelly ne sait pas si une porte est ouverte ou fermée).

### Verrouillage anti-concurrence

Avant l'appel Shelly, un `UPDATE ... WHERE status=IDLE` conditionnel tente de passer le statut à `IN_PROGRESS`. Un seul worker gunicorn peut gagner cette écriture — la base de données sérialise elle-même la concurrence, pas besoin de `select_for_update` explicite.

- Si le verrou échoue (déjà `IN_PROGRESS`) → `PulseSwitchBusyError`.
- Le verrou protège contre les **workers gunicorn concurrents**, pas contre un double-clic utilisateur (jugé sans risque : l'utilisateur est physiquement devant la porte).
- Le statut est remis à `IDLE` dans un bloc `finally`, succès ou échec — évite un blocage permanent du PulseSwitch en cas d'erreur Shelly.

### Durée d'impulsion

`PULSE_SECONDS = 1`, codée en dur dans le service — comportement de définition d'un PulseSwitch, pas une configuration par instance.

---

## API REST

```
GET  /api/equipment/pulse-switches/              # Public — liste avec id, name, status
POST /api/equipment/pulse-switches/<pk>/trigger/  # Authentifié — déclenche l'impulsion
```

**Réponses de `trigger/` :**

| Code | Cas |
|------|-----|
| 200 | Impulsion envoyée avec succès |
| 404 | PulseSwitch introuvable |
| 409 | Déjà en cours (`PulseSwitchBusyError`) |
| 400 | Autre erreur (`PulseSwitchError` — pas de Shelly assigné, erreur driver, etc.) |

---

## Administration Django

**ShellyAdmin** (`actuators`) :
- Champ en lecture seule "État en direct" : état du relais + état de l'entrée SW, interrogés en direct sur le device (`"Injoignable : ..."` si le Shelly ne répond pas).
- Actions : configurer la borne SW comme capteur / comme interrupteur.

**PulseSwitchAdmin** (`equipment`) :
- Action "Déclencher l'impulsion" en masse sur la sélection.
- `status` et `last_triggered_at` en lecture seule.

---

## Frontend

🚧 **En construction.**

Le pilotage est pour l'instant réservé à l'admin Django. Le bouton frontend "pilotage simple" est volontairement en pause tant qu'il n'y a pas de retour d'état fiable (capteur de position) : déclencher une porte à distance sans savoir si elle est ouverte ou fermée est jugé risqué.

Pistes UI envisagées pour plus tard, non tranchées :
- Une card sur la page Home plutôt qu'une page dédiée (cohérent avec l'agrégation déjà en place pour les pièces).
- Une interaction en pression maintenue (long-press) plutôt qu'un bouton simple ou une confirmation, pour limiter le risque de déclenchement accidentel sans ajouter de friction lourde.
- L'affichage du bouton (libellé "ouvrir"/"fermer" vs bouton neutre) dépendra de la disponibilité d'un état de position lu via un capteur câblé sur la borne SW.

---

## Prochaine étape (hors code)

Câblage matériel d'un reed switch magnétique sur la borne SW du Shelly de la porte de garage.

**Procédure impérative, dans l'ordre :**
1. `set_sw_terminal_as_sensor()` (via l'action admin) — détache la borne SW du relais.
2. Câblage du reed switch sur SW.

Câbler avant l'étape 1 risque de déclencher la porte au branchement.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
