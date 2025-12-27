# Pilotage des radiateurs - Fil pilote

Système de contrôle des radiateurs électriques via fil pilote avec gestion intelligente du délestage.

---

## Vue d'ensemble

Le module actuators pilote les radiateurs électriques par fil pilote en utilisant un circuit MCP23017 (I2C). Le système gère automatiquement le délestage en cas de risque de dépassement de puissance souscrite.

---

## Architecture découplée - Software vs Hardware

### Principe fondamental

Le système maintient un **découplage strict** entre l'état logiciel (intention du système) et l'état matériel (état physique réel du radiateur).

**État software :**
- `requested_state` : intention du système stockée en base de données
- Modifié par les workers Django, les plannings horaires, les automatismes

**État hardware :**
- `actual_state` : état physique réel du radiateur
- Reflète l'état des pins MCP23017

### Pourquoi ce découplage ?

**Problème de concurrence :**
- Gunicorn utilise plusieurs workers Django en parallèle
- Une seule carte MCP23017 physique sur le bus I2C
- Si chaque worker pilote directement la carte → conflits I2C et état incohérent

**Solution :**
- Les workers Django modifient uniquement `requested_state` en base de données
- Un processus unique (scheduler ou listener) synchronise périodiquement DB ↔ Hardware
- Aucun conflit d'accès I2C possible

### Processus autorisés à piloter le hardware

**Scheduler (synchronisation périodique) :**
- Tâche exécutée toutes les 1 minute
- Synchronisation systématique DB → Hardware → DB
- Processus systemd unique, pas de conflit

**Listener Teleinfo (synchronisation d'urgence) :**
- Peut forcer une synchronisation immédiate en cas de délestage
- Déclenché si puissance disponible < seuil de sécurité
- Processus systemd unique, pas de conflit

**Aucun autre processus ne doit accéder au driver MCP23017.**

---

## Driver MCP23017

### Communication I2C

Le MCP23017 est un expandeur GPIO I2C offrant 16 pins de sortie.

**Configuration :**
- Bus I2C du Raspberry Pi (SDA/SCL)
- Adresse I2C par défaut
- 16 pins disponibles (0-15)

### Logique fil pilote inversée

**IMPORTANT :** La logique est inversée à cause de la carte électronique custom.

**Fonctionnement fil pilote :**
- Carte custom génère une demi-alternance négative pour mettre le radiateur en mode hors-gel
- Pin MCP23017 **HIGH** → Carte génère signal → Radiateur en **hors-gel (OFF)**
- Pin MCP23017 **LOW** → Pas de signal → Radiateur fonctionne **normalement (ON)**

**Mapping :**
```
Software (DB)     →  Pin MCP23017  →  Hardware (Radiateur)
requested_state=ON  →  LOW (False)  →  actual_state=ON
requested_state=OFF →  HIGH (True)  →  actual_state=OFF
```

Le mapper `RadiatorStateMapper` gère cette inversion de manière transparente.

### Mode UNPLUGGED

En développement, le mode `UNPLUGGED=True` simule le hardware sans accès I2C réel.

---

## Modèle Radiator

### Les trois états

**requested_state (État demandé) :**
- `ON` : Le système souhaite chauffer
- `OFF` : Le système souhaite arrêter
- `LOAD_SHED` : Délestage forcé (équivalent à OFF)

**actual_state (État réel) :**
- `ON` : Le radiateur chauffe effectivement
- `OFF` : Le radiateur est en hors-gel
- `UNDEFINED` : État inconnu (erreur de communication)

**error (Erreur) :**
- Message d'erreur en cas de problème I2C ou MCP23017
- `None` si tout fonctionne correctement

### Importance du radiateur

Détermine l'ordre de délestage en cas de dépassement de puissance :

| Importance | Valeur | Ordre de coupure |
|------------|--------|------------------|
| CRITICAL | 0 | Jamais coupé |
| HIGH | 1 | Coupé en dernier |
| MEDIUM | 2 | Coupé avant HIGH |
| LOW | 3 | Coupé en premier |

### Champs du modèle

```python
name             # Nom du radiateur
power            # Puissance en watts
control_pin      # Pin MCP23017 (0-15)
importance       # Niveau d'importance (0-3)
requested_state  # État demandé (ON/OFF/LOAD_SHED)
actual_state     # État réel (ON/OFF/UNDEFINED)
last_requested   # Timestamp de dernière modification
error            # Message d'erreur (nullable)
```

---

## Synchronisation

### Flux de synchronisation

**Phase 1 : DB → Hardware**
1. Lecture de tous les radiateurs (id, control_pin, requested_state)
2. Pour chaque radiateur : appliquer `requested_state` sur le pin MCP23017
3. Le mapper convertit automatiquement (ON → LOW, OFF/LOAD_SHED → HIGH)

**Phase 2 : Hardware → DB**
1. Lecture de l'état de tous les pins MCP23017
2. Pour chaque pin : conversion vers `actual_state` via mapper
3. Mise à jour des radiateurs dont `actual_state` a changé
4. Mise à jour du champ `error` en cas de problème

### Déclenchement

**Automatique (scheduler) :**
```python
# Toutes les 1 minute
RadiatorSyncService.synchronize_database_and_hardware()
```

**Manuel (urgence) :**
```python
# Appelé par le listener Teleinfo en cas de délestage
ensure_power_not_exceeded()
RadiatorSyncService.synchronize_database_and_hardware()
```

---

## Délestage (Load Shedding)

### Principe

Le délestage coupe automatiquement des radiateurs pour éviter un dépassement de puissance souscrite.

### Déclenchement

**Condition :**
```
Puissance disponible < POWER_SAFETY_MARGIN (2000W)
```

**Qui déclenche :**
Le listener Teleinfo détecte la puissance disponible insuffisante et appelle `manage_load_shedding()`.

### Sélection des radiateurs à couper

**Algorithme :**
1. Liste des radiateurs allumés triés par importance croissante puis puissance décroissante
2. Coupure séquentielle jusqu'à récupérer assez de puissance
3. Les radiateurs CRITICAL ne sont jamais coupés

**Cas particulier :**
Si la puissance disponible est inconnue (Teleinfo en erreur), tous les radiateurs sauf CRITICAL et HIGH sont coupés préventivement.

### Application immédiate

Après sélection, le délestage est appliqué immédiatement :
1. Mise à jour `requested_state=LOAD_SHED` en DB
2. Synchronisation forcée avec le hardware
3. Pas d'attente du scheduler

---

## Configuration via Admin Django

### Interface d'administration

```
/backend/admin/actuators/radiator/
```

**Champs configurables :**
- Nom du radiateur
- Puissance (watts)
- Pin MCP23017 (0-15, unique)
- Importance (CRITICAL/HIGH/MEDIUM/LOW)
- État demandé (ON/OFF)

**Champs en lecture seule :**
- État réel
- Dernière demande
- Erreur

### Actions en masse

**Allumer les radiateurs sélectionnés :**
Met `requested_state=ON` pour tous les radiateurs sélectionnés.

**Éteindre les radiateurs sélectionnés :**
Met `requested_state=OFF` pour tous les radiateurs sélectionnés.

La synchronisation hardware sera effectuée au prochain cycle du scheduler (max 1 minute).

---

## Gestion des erreurs

### Types d'erreurs

**Erreurs I2C :**
- Bus I2C non accessible
- Perte de communication avec le MCP23017
- `actual_state=UNDEFINED`, erreur stockée

**Erreurs de pin :**
- Pin invalide (< 0 ou > 15)
- État appliqué différent de l'état demandé
- Erreur stockée avec détails

**Reconnexion automatique :**
Le driver tente de se reconnecter à chaque appel si la connexion I2C est perdue.

### Logs

```bash
# Logs de synchronisation
sudo journalctl -u housebrain-periodic -f | grep RADIATORSYNC

# Logs de délestage
sudo journalctl -u teleinfo-listener -f | grep LOADSHEDDING

# Logs du driver MCP23017
sudo journalctl -u housebrain-periodic -f | grep MCPDRIVER
```

---

## Configuration hardware

Documentation du branchement fil pilote avec MCP23017 : [À venir - docs/hardware/mcp23017_heating.md]

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
