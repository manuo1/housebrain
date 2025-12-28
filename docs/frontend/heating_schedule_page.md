# Heating Schedule Page - Planification du chauffage

Page d'édition des plannings de chauffage journaliers avec calendrier, timeline interactive et système de duplication.

---

## Vue d'ensemble

Interface complète de gestion des plannings de chauffage permettant de créer, modifier et dupliquer des créneaux horaires par pièce.

**Route :** `/heating-schedule`

**Fonctionnalités principales :**
- Calendrier mensuel avec visualisation des états de planification
- Sélection des pièces à afficher/éditer
- Édition graphique des créneaux horaires (timeline)
- Undo/redo avec sauvegarde backend
- Duplication de plannings (jour ou semaine)

---

## Architecture

### Structure des fichiers

```
src/
├── pages/
│   └── HeatingSchedulePage.jsx            # Page principale (orchestration)
├── hooks/
│   └── HeatingSchedulePage/
│       └── useHeatingPlanHistory.js       # État + undo/redo + save
├── models/
│   ├── HeatingCalendar.js                 # Modèle calendrier
│   └── DailyHeatingPlan.js                # Modèle planning journalier
├── services/
│   ├── fetchHeatingCalendar.js            # GET calendar
│   ├── fetchDailyHeatingPlan.js           # GET plan
│   ├── saveDailyHeatingPlan.js            # POST plan
│   └── duplicateHeatingPlan.js            # POST duplicate
└── components/HeatingSchedulePage/
    ├── Calendar/                           # Voir heating_calendar.md
    ├── RoomsSelector/                      # Voir heating_calendar.md
    ├── Timeline/                           # Voir heating_timeline.md
    └── Duplication/                        # Voir heating_duplication.md
```

### Layout 3 zones

```
┌──────────────┬───────────────────────┬──────────────┐
│  Calendar    │   DateHeader          │  Duplication │
│              │   Timeline            │  Panel       │
│  Rooms       │   (créneaux)          │              │
│  Selector    │                       │              │
└──────────────┴───────────────────────┴──────────────┘
  Sidebar Left      Main Content         Sidebar Right
```

---

## Page HeatingSchedulePage

**Fichier :** `src/pages/HeatingSchedulePage.jsx`

### Responsabilités

- Orchestration des 3 zones (Calendar, Timeline, Duplication)
- Gestion de la date et du mois sélectionnés
- Gestion de la sélection des pièces
- Bridge entre Timeline et le hook d'historique
- Rafraîchissement du calendrier après duplication

### État principal

```javascript
const { dailyPlan, loading, canUndo, hasChanges, undo, save, applyChange } =
  useHeatingPlanHistory(selectedDate);
```

### Flux de données

**Chargement initial :**
1. Fetch calendrier mois courant
2. Sélectionne aujourd'hui
3. Hook charge le planning du jour
4. Auto-sélectionne toutes les pièces

**Changement de date :**
- User clique jour → `selectedDate` change → Hook refetch automatique

**Modification créneaux :**
- Timeline → `handleSlotUpdate()` → `applyChange(newPlan)` → History stack

**Sauvegarde :**
- User clique "Enregistrer" → `save()` → POST backend → Refetch → Clear history

---

## Hook useHeatingPlanHistory

**Fichier :** `src/hooks/HeatingSchedulePage/useHeatingPlanHistory.js`

### Principe

Gère l'état du planning avec historique pour undo/redo et sauvegarde backend.

### Fonctionnement

**État géré :**
- `dailyPlan` : État actuel (DailyHeatingPlan)
- `initialPlan` : État initial après fetch/save
- `history` : Stack pour undo (array de plans précédents)

**Fonctions exposées :**
- `applyChange(newPlan)` : Pousse état actuel dans history, applique nouveau plan
- `undo()` : Restaure dernier état de l'historique
- `save()` : POST backend + refetch + clear history

**Auto-fetch :**
Le hook fetch automatiquement le planning à chaque changement de `selectedDate`.

**Point technique :**
Utilise `useRef` pour éviter stale closure dans `save()` (accède à la dernière valeur de `dailyPlan`).

---

## Modèles

### HeatingCalendar

**Fichier :** `src/models/HeatingCalendar.js`

```javascript
{
  year: number,
  month: number,
  today: SimpleDate,
  days: [{ date: SimpleDate, status: 'empty'|'normal'|'different' }]
}
```

**Status des jours :**
- `empty` : Pas de planning
- `normal` : Planning = template de la pièce
- `different` : Planning personnalisé

### DailyHeatingPlan

**Fichier :** `src/models/DailyHeatingPlan.js`

```javascript
{
  date: "YYYY-MM-DD",
  rooms: [
    {
      id: number,
      name: string,
      slots: [{ start: "HH:MM", end: "HH:MM", value: "20.5"|"on"|"off" }]
    }
  ]
}
```

**Contrainte importante :** Tous les créneaux d'une même pièce doivent être du même type (température OU on/off).

---

## Services API

### fetchHeatingCalendar(year, month)

**Endpoint :** `GET /api/heating/calendar/?year=X&month=Y`

Paramètres `null` = mois en cours. Retourne `HeatingCalendar`.

### fetchDailyHeatingPlan(date)

**Endpoint :** `GET /api/heating/plans/daily/?date=YYYY-MM-DD`

Retourne `DailyHeatingPlan`.

### saveDailyHeatingPlan(dailyPlan, accessToken, refreshCallback)

**Endpoint :** `POST /api/heating/plans/daily/`

**Transformation :** Convertit le modèle frontend en format backend :
- Détermine automatiquement le type (`temp` ou `onoff`) selon la valeur
- Groupe par `room_id` avec array de `slots`

Utilise `fetchWithAuth` pour refresh automatique du token si 401.

### duplicateHeatingPlan(duplicationData, accessToken, refreshCallback)

**Endpoint :** `POST /api/heating/plans/duplicate/`

**Payload :**
```javascript
{
  type: "day"|"week",
  source_date: "YYYY-MM-DD",
  repeat_since: "YYYY-MM-DD",
  repeat_until: "YYYY-MM-DD",
  room_ids: [1, 2, 3],
  weekdays: ["monday", "friday"] // Si type="day" uniquement
}
```

---

## Gestion de l'authentification

Les composants d'édition (Timeline, SaveActions, DuplicationPanel) vérifient la présence de `user` :
- Si absent → Blocage des interactions + message "Vous devez être connecté"
- Si présent → Fonctionnalités activées

Tous les services d'écriture utilisent `fetchWithAuth` qui gère le refresh token automatique en cas de 401.

---

## Flux utilisateur

### Éditer un planning

1. Sélectionner un jour dans le calendrier
2. Optionnel : Déselectionner des pièces
3. Cliquer sur la timeline pour créer/modifier des créneaux
4. Utiliser "Annuler" si besoin (undo)
5. Cliquer "Enregistrer" pour sauvegarder

### Dupliquer un planning

1. Sélectionner le jour source
2. Déselectionner les pièces à exclure
3. Configurer la duplication dans le panneau de droite (mode, dates, jours)
4. Vérifier le récapitulatif
5. "Appliquer la duplication" → Confirmation → Backend duplique
6. Calendrier se rafraîchit automatiquement

---

## Composants (voir docs dédiées)

- **Timeline - Éditeur de créneaux :** [heating_timeline.md](./heating_timeline.md)
- **Calendrier et sélection :** [heating_calendar.md](./heating_calendar.md)
- **Système de duplication :** [heating_duplication.md](./heating_duplication.md)

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
