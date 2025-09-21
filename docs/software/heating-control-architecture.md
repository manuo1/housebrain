# Architecture du Contrôle de Chauffage

## Vue d'ensemble

Le système de contrôle de chauffage d'Housebrain gère les radiateurs à travers une architecture multi-couches qui sépare le contrôle hardware, la gestion des données, et la logique métier.

## Composants de l'Architecture

### 1. Driver MCP23017

**Rôle :** Interface pure avec le hardware I2C

**Caractéristiques clés :**
- `set_pin(pin_number, state)` - Change l'état du pin avec vérification automatique
- `get_pin(pin_number)` - Lit l'état réel du hardware
- Exception `MCP23017Error` avec `pin_state` pour diagnostiquer les erreurs
- Support `UNPLUGGED_MODE` pour le développement sans hardware physique
- Pattern Singleton pour éviter les conflits I2C

**Principe de conception :** Le driver ne connaît que les pins (0-15), pas la notion de "radiateur". Il fournit une abstraction propre du GPIO expander MCP23017.

**Gestion d'erreur :**
- Les échecs de connexion sont détectés et remontés
- Vérification de l'état du pin après chaque écriture
- Dégradation en mode unplugged

### 2. Modèle Radiator

**Rôle :** Interface de données entre les intentions système et la réalité hardware

**Champs clés :**
```python
requested_state = CharField()  # OFF/ON/LOAD_SHED (intention système)
actual_state = CharField()     # OFF/ON/UNDEFINED (réalité hardware)  
last_requested = DateTimeField()  # Traçabilité des décisions
control_pin = PositiveSmallIntegerField()  # Mapping pin MCP23017
priority = IntegerChoices()  # Priorité de délestage
```

**Logique des états :**
- `requested_state` : Ce que le système veut faire
- `actual_state` : Ce que le hardware fait réellement
- `requested_state == LOAD_SHED` vs `requested_state == OFF` : Distinction d'une volonté d'éteindre le radiateur depuis "délestage réseau" ou "régulation normale"

**États possibles :**
- `requested_state` : `OFF`, `ON`, `LOAD_SHED`
- `actual_state` : `OFF`, `ON`, `UNDEFINED` (en cas d'erreur de communication)

### 3. Radiator Manager (Service)

**Rôle :** Pont entre le modèle Django et le driver MCP

**Responsabilités :**
- `set_radiator_state(radiator_id, new_state)` → Pilote le driver + met à jour la BDD
- En charge de mettre à jour en BDD `requested_state` `actual_state` et `last_requested` 
- Gestion des erreurs hardware → Mise à jour cohérente du modèle en fonction du retour du Driver MCP23017
- Interface unique pour tous les changements d'état hardware
- Garantit la cohérence entre modèle et hardware


**Principe :** Un seul point d'accès pour modifier l'état des radiateurs, évitant les incohérences.

### 4. Heating Manager (Service)

**Rôle :** Logique métier de régulation thermique

**Responsabilités :**
- Lit les consignes de température et plannings
- Calcule quels radiateurs allumer/éteindre selon les besoins
- Vérifie la puissance disponible (via cache Redis)
- Délègue l'exécution au Radiator Manager
- Gère la logique de priorisation

**Principe :** Intelligence thermique sans connaître les détails hardware.

## Architecture Globale

### Flux de données

```
API Django → Modèle Radiator (requested_state)
     ↓
Heating Manager → Radiator Manager → Driver MCP → Hardware MCP23017
     ↑                    ↓
Cache Redis        Modèle Radiator (actual_state)
```

### Séparation des responsabilités

1. **API Django** : Interface utilisateur, ne touche que la BDD
2. **Heating Manager** : Logique de régulation, décisions thermiques
3. **Radiator Manager** : Orchestration hardware + données
4. **Driver MCP23017** : Communication I2C pure
5. **Modèle Radiator** : Persistance des états et intentions

## Gestion des Conflits

### Problème initial
- 3 workers Gunicorn = 3 processus Django simultanés
- Accès concurrent au bus I2C = conflits hardware

### Solution adoptée
- **API Django** : Modification des états en BDD uniquement
- **Services uniques** (cron + teleinfo listener) : Seuls à piloter le hardware

## Gestion du Délestage

### Déclenchement
1. **Teleinfo Listener** détecte surconsommation (cycle ~1.2s)
2. **Service de délestage** sélectionne les radiateurs à éteindre (par priorité)
3. **Radiator Manager** exécute les arrêts via driver MCP
4. **États résultants** : `requested_state=LOAD_SHED`, `actual_state=OFF`

### Récupération
1. **Heating Manager** vérifie puissance disponible
2. Si suffisante, peut rallumer les radiateurs délestés
3. Transition : `LOAD_SHED` → `ON` si conditions remplies

## Cas d'Usage Interface Utilisateur

### États visibles utilisateur

- Allumage Manuel : `requested_state == ON & actual_state == OFF` : "Allumage en cours..." (attend le prochain cycle du heating manager pour appliquer le changements)
- `requested_state = ON`, `actual_state = ON` : "Allumé"  
- `requested_state = LOAD_SHED`, `actual_state = OFF` : "Délestage réseau"
- `actual_state = UNDEFINED` : "Erreur de communication"
