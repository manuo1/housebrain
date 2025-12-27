# Heating - Planification du chauffage

Système de gestion des plannings de chauffage par pièce avec patterns réutilisables.

---

## Vue d'ensemble

Le module heating planning permet de définir des plannings horaires de chauffage pour chaque pièce. Il utilise un système de patterns réutilisables pour optimiser le stockage et faciliter la duplication.

---

## Modèles

### HeatingPattern - Patterns réutilisables

Un pattern définit une configuration horaire complète pour une journée.

**Champs :**
```python
slots         # JSON: liste des créneaux horaires
slots_hash    # MD5: hash pour déduplication (unique)
created_at    # Timestamp de création
```

**Structure d'un slot :**
```json
{
  "start": "07:00",
  "end": "09:00",
  "type": "temp",
  "value": 20.5
}
```

**Types de slots :**

**TEMPERATURE (type: "temp") :**
- Valeur : température en °C (float)
- Mode thermostat activé
- Exemple : `{"start": "07:00", "end": "22:00", "type": "temp", "value": 19.5}`

**ONOFF (type: "onoff") :**
- Valeur : "on" ou "off" (string)
- Chauffage direct sans régulation
- Exemple : `{"start": "07:00", "end": "22:00", "type": "onoff", "value": "on"}`

**Contraintes :**
- Tous les slots d'un pattern doivent avoir le même type
- Pas de chevauchement entre les créneaux
- Format horaire : HH:MM
- start < end pour chaque créneau
- Créneaux triés par ordre chronologique

### RoomHeatingDayPlan - Planning journalier

Associe un pattern à une pièce pour un jour donné.

**Champs :**
```python
room              # FK vers Room
date              # Date du planning
heating_pattern   # FK vers HeatingPattern
created_at        # Timestamp création
updated_at        # Timestamp dernière modification
```

**Contrainte :**
- Unique (room, date) : une seule configuration par pièce par jour

---

## Déduplication des patterns

### Principe

Les patterns identiques sont automatiquement dédupliqués via un hash MD5 calculé sur les slots.

**Avantages :**
- Économie de stockage
- Facilite la duplication de plannings
- Permet de compter les usages

### Mécanisme

**Calcul du hash :**
```python
slots_str = json.dumps(slots, sort_keys=True, ensure_ascii=False)
slots_hash = hashlib.md5(slots_str.encode("utf-8")).hexdigest()
```

**Création/récupération :**
```python
pattern, created = HeatingPattern.get_or_create_from_slots(slots)
```

Si un pattern avec le même hash existe déjà, il est réutilisé.

### Protection des patterns

Un pattern utilisé par plusieurs `RoomHeatingDayPlan` ne peut pas être modifié. Il faut en créer un nouveau.

---

## Périodes non définies

**IMPORTANT :** Une période sans créneau défini entraîne automatiquement un chauffage éteint.

Exemple :
```json
[
  {"start": "07:00", "end": "09:00", "type": "temp", "value": 19.5},
  {"start": "18:00", "end": "22:00", "type": "temp", "value": 20.0}
]
```

Résultat :
- 00:00 → 07:00 : OFF
- 07:00 → 09:00 : Thermostat 19.5°C
- 09:00 → 18:00 : OFF
- 18:00 → 22:00 : Thermostat 20.0°C
- 22:00 → 24:00 : OFF

---

## API REST

### Calendrier mensuel

```
GET /api/heating/calendar/?year=2025&month=12
```

Retourne un calendrier avec le statut de chaque jour :

**Statuts :**

**EMPTY :**
- Aucun planning défini pour ce jour
- Aucune pièce n'a de RoomHeatingDayPlan

**NORMAL :**
- Planning identique à la semaine précédente
- Toutes les pièces ont le même hash de pattern que le même jour 7 jours avant
- Indique une routine hebdomadaire stable

**DIFFERENT :**
- Planning différent de la semaine précédente
- Au moins une pièce a un pattern différent du même jour 7 jours avant
- Peut indiquer une modification ponctuelle ou une exception à la routine

**Exemple :**
```
Lundi 16 déc : Pattern A pour Salon
Lundi 23 déc : Pattern A pour Salon → NORMAL

Lundi 16 déc : Pattern A pour Salon
Lundi 23 déc : Pattern B pour Salon → DIFFERENT
```

**Réponse :**
```json
{
  "year": 2025,
  "month": 12,
  "today": "2025-12-27",
  "days": [
    {"date": "2025-12-01", "status": "normal"},
    {"date": "2025-12-02", "status": "different"},
    ...
  ]
}
```

### Planning journalier

**Lecture :**
```
GET /api/heating/plans/daily/?date=2025-12-27
```

**Réponse :**
```json
{
  "date": "2025-12-27",
  "rooms": [
    {
      "room_id": 1,
      "name": "Salon",
      "slots": [
        {"start": "07:00", "end": "09:00", "value": "19.5"},
        {"start": "18:00", "end": "22:00", "value": "20.0"}
      ]
    }
  ]
}
```

**Création/Mise à jour :**
```
POST /api/heating/plans/daily/
```

**Body :**
```json
{
  "plans": [
    {
      "room_id": 1,
      "date": "2025-12-27",
      "slots": [
        {"start": "07:00", "end": "09:00", "type": "temp", "value": 19.5}
      ]
    }
  ]
}
```

**Réponse :**
```json
{
  "created": 2,
  "updated": 1
}
```

### Duplication de plannings

```
POST /api/heating/plans/duplicate/
```

**Types de duplication :**

**DAY - Duplication d'un jour :**

Duplique le planning d'un jour source vers plusieurs jours cibles sélectionnés par jour de la semaine.

**Principe :**
1. Source : planning du lundi 23 décembre
2. Cible : tous les lundis, mercredis et vendredis du 30 décembre au 15 janvier
3. Résultat : le planning du lundi 23 est copié sur tous ces jours

**Cas d'usage :** Répéter un jour type (ex: programme du lundi) sur plusieurs occurrences.

**Body :**
```json
{
  "type": "day",
  "source_date": "2025-12-27",
  "repeat_since": "2025-12-28",
  "repeat_until": "2026-01-15",
  "weekdays": ["monday", "wednesday", "friday"],
  "room_ids": [1, 2, 3]
}
```

**WEEK - Duplication d'une semaine :**

Duplique une semaine complète (7 jours) vers plusieurs semaines cibles.

**Principe :**
1. Source : semaine du 23 au 29 décembre
2. Cible : toutes les semaines du 30 décembre au 20 janvier
3. Résultat :
   - Lundi 23 → tous les lundis de la période
   - Mardi 24 → tous les mardis de la période
   - Mercredi 25 → tous les mercredis de la période
   - etc.

**Cas d'usage :** Répéter une routine hebdomadaire complète sur plusieurs semaines.

**Body :**
```json
{
  "type": "week",
  "source_date": "2025-12-23",
  "repeat_since": "2025-12-30",
  "repeat_until": "2026-01-20",
  "room_ids": [1, 2, 3]
}
```

**Notes :**
- La `source_date` peut être n'importe quel jour de la semaine source
- Le système récupère automatiquement toute la semaine contenant cette date
- Les dates cibles sont alignées automatiquement (lundi source → lundis cibles)

**Contraintes :**
- `repeat_since` > `source_date`
- `repeat_until` > `repeat_since`
- Pour WEEK : minimum 6 jours entre since et until
- Maximum 365 jours entre since et until

**Réponse :**
```json
{
  "created/updated": 42
}
```

---

## Administration Django

### HeatingPattern

```
/backend/admin/heating/heatingpattern/
```

**Affichage :**
- Aperçu des slots (4 premiers créneaux)
- Nombre d'utilisations (compteur de RoomHeatingDayPlan)
- Date de création

**Création/Modification :**
- Édition JSON directe des slots
- Validation automatique (format, chevauchements, type)
- Hash calculé automatiquement

### RoomHeatingDayPlan

```
/backend/admin/heating/roomheatingdayplan/
```

**Affichage :**
- Liste par date (hiérarchie date)
- Filtres : date, pièce, pattern
- Autocomplete pour pièce et pattern

**Actions en masse :**
- Duplication vers une date cible

**Détails :**
- Affichage complet des créneaux du pattern associé

---

## Validation des données

### Validation des slots

**Format requis :**
- Slots = liste de dictionnaires
- Chaque slot : `{start, end, type, value}`
- Format horaire : HH:MM
- start < end

**Cohérence :**
- Type unique par pattern (tous temp OU tous onoff)
- Pas de chevauchement de créneaux
- Valeurs cohérentes avec le type

**Valeurs selon type :**
- TEMPERATURE : nombre (int ou float)
- ONOFF : chaîne "on" ou "off"

### Erreurs courantes

**"Slots overlap" :**
Deux créneaux se chevauchent. Vérifier l'ordre et les horaires.

**"All slots must have the same type" :**
Mélange de type temp et onoff. Corriger pour uniformiser.

**"Slot value does not match its type" :**
Valeur incorrecte (ex: string dans un slot temp).

**"An identical heating pattern already exists" :**
Un pattern identique existe déjà et sera réutilisé automatiquement.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
