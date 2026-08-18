# Heating Schedule Page - Planification du chauffage

Page d'édition des plannings de chauffage journaliers avec calendrier, timeline interactive et duplication via chat IA.

---

## Vue d'ensemble

Interface complète de gestion des plannings de chauffage permettant de créer, modifier et dupliquer des créneaux horaires par pièce.

**Route :** `/heating-schedule`

**Fonctionnalités principales :**
- Calendrier mensuel avec visualisation des états de planification
- Sélection des pièces à afficher/éditer
- Édition graphique des créneaux horaires (timeline)
- Modification de créneaux via instruction IA en langage naturel
- Undo/redo avec sauvegarde backend
- Duplication de plannings via chat IA conversationnel

---

## Architecture

### Structure des fichiers

```
src/
├── pages/
│   └── HeatingSchedulePage.tsx            # Page principale (orchestration)
├── hooks/
│   └── HeatingSchedulePage/
│       └── useHeatingPlanHistory.ts       # État + undo/redo + save
├── models/
│   ├── HeatingCalendar.ts                 # Modèle calendrier
│   └── DailyHeatingPlan.ts                # Modèle planning journalier
├── services/
│   ├── fetchHeatingCalendar.ts            # GET calendar
│   ├── fetchDailyHeatingPlan.ts           # GET plan
│   ├── saveDailyHeatingPlan.ts            # POST plan
│   ├── applyAiPlanModification.ts         # POST modify (IA)
│   └── duplicateHeatingPlanAi.ts          # POST duplicate (chat IA)
└── components/HeatingSchedulePage/
    ├── Calendar/                           # Voir heating_calendar.md
    ├── RoomsSelector/                      # Voir heating_calendar.md
    ├── Timeline/                           # Voir heating_timeline.md
    ├── AiPlanInput/                        # Voir ai_heating_modification.md
    └── DuplicationChat/                    # Voir heating_duplication.md
```

### Layout 3 zones

```
┌──────────────┬───────────────────────┬──────────────┐
│  Calendar    │   DateHeader          │  Duplication │
│              │   AiPlanInput         │  Chat        │
│  Rooms       │   Timeline            │              │
│  Selector    │   (créneaux)          │              │
└──────────────┴───────────────────────┴──────────────┘
  Sidebar Left      Main Content         Sidebar Right
```

`.rightPanel` (sidebar droite) n'est rendu que si l'utilisateur est connecté. En mobile (breakpoint `lg`), les 3 zones passent en colonne — `.rightPanel` reste affiché, en dernière position sous le contenu principal.

---

## Page HeatingSchedulePage

**Fichier :** `src/pages/HeatingSchedulePage.tsx`

### Responsabilités

- Orchestration des zones (Calendar, RoomsSelector, AiPlanInput, Timeline, DuplicationChat)
- Gestion de la date et du mois sélectionnés
- Gestion de la sélection des pièces
- Bridge entre Timeline et le hook d'historique
- Rafraîchissement du calendrier après duplication IA (`handleDuplicationSuccess`)

### État principal

```typescript
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

**Modification créneaux (manuelle) :**
- Timeline → `handleSlotUpdate()` → reconstruit `DailyHeatingPlan` via son constructeur (pas de clonage de prototype, garde `raw` synchronisé) → `applyChange(newPlan)` → History stack

**Modification via IA :**
- `AiPlanInput` → `handleAiRequest(instruction)` → `applyAiPlanModification({instruction, plan: dailyPlan.raw}, ...)` → `applyChange(newPlan)` — même chemin que toute modification manuelle

**Duplication via IA :**
- `DuplicationChat` gère son propre état conversationnel en interne (voir [heating_duplication.md](./heating_duplication.md)) ; en cas de succès, appelle `onDuplicationSuccess` → `handleDuplicationSuccess()` refetch le calendrier du mois courant

**Sauvegarde :**
- User clique "Enregistrer" → `save()` → POST backend → Refetch → Clear history

---

## Hook useHeatingPlanHistory

**Fichier :** `src/hooks/HeatingSchedulePage/useHeatingPlanHistory.ts`

### Principe

Gère l'état du planning avec historique pour undo et sauvegarde backend.

### Fonctionnement

**État géré :**
- `dailyPlan` : État actuel (`DailyHeatingPlan`)
- `history` : Stack pour undo (array de plans précédents)

**Fonctions exposées :**
- `applyChange(newPlan)` : Pousse état actuel dans history, applique nouveau plan
- `undo()` : Restaure dernier état de l'historique
- `save()` : POST backend + refetch + clear history
- `canUndo`/`hasChanges` : dérivés de `history.length > 0`

**Auto-fetch :**
Le hook fetch automatiquement le planning à chaque changement de `selectedDate`.

**Point technique :**
Utilise `useRef` (`dailyPlanRef`) pour éviter stale closure dans `save()` (accède à la dernière valeur de `dailyPlan`).

---

## Modèles

### HeatingCalendar

**Fichier :** `src/models/HeatingCalendar.ts`

```typescript
{
  year: number | null,
  month: number | null,
  today: SimpleDate | null,
  days: { date: SimpleDate | null, status: DayStatusType }[]
}
```

**Status des jours (`DayStatus`) :**
- `EMPTY` : Pas de planning
- `NORMAL` : Planning = même hash que la semaine précédente
- `DIFFERENT` : Planning différent de la semaine précédente

### DailyHeatingPlan

**Fichier :** `src/models/DailyHeatingPlan.ts`

```typescript
{
  date: string | null,
  rooms: {
    id: number | null,
    name: string,
    slots: { start: string, end: string, value: number | string | null }[]
  }[]
}
```

**Contrainte importante :** Tous les créneaux d'une même pièce doivent être du même type (température OU on/off).

---

## Services API

### fetchHeatingCalendar(year, month)

**Endpoint :** `GET /api/heating/calendar/?year=X&month=Y`

Paramètres `undefined` = mois en cours. Retourne `HeatingCalendar`.

### fetchDailyHeatingPlan(date)

**Endpoint :** `GET /api/heating/plans/daily/?date=YYYY-MM-DD`

Retourne `DailyHeatingPlan`.

### saveDailyHeatingPlan(dailyPlan, accessToken, refreshCallback)

**Endpoint :** `POST /api/heating/plans/daily/`

**Transformation :** Convertit le modèle frontend en format backend :
- Détermine automatiquement le type (`temp` ou `onoff`) selon la valeur
- Groupe par `room_id` avec array de `slots`

Utilise `fetchWithAuth` pour refresh automatique du token si 401.

### applyAiPlanModification(payload, accessToken, refreshCallback)

**Endpoint :** `POST /api/ai/heating/modify/` — voir [ai_heating_modification.md](./ai_heating_modification.md).

### duplicateHeatingPlanAi(sourceDate, echanges, accessToken, refreshCallback, step, data)

**Endpoint :** `POST /api/ai/heating/duplicate/` — protocole conversationnel (`echanges`/`step`/`data`), voir [heating_duplication.md](./heating_duplication.md).

---

## Gestion de l'authentification

Les composants d'édition (Timeline, TimelineSaveActions, AiPlanInput, DuplicationChat) ne sont rendus que si `user` est présent (sauf Timeline, toujours affichée mais en lecture seule) :
- Si absent → message "Vous devez être connecté pour modifier ces éléments", zones IA/duplication masquées
- Si présent → Fonctionnalités activées

Tous les services d'écriture utilisent `fetchWithAuth` qui gère le refresh token automatique en cas de 401.

---

## Flux utilisateur

### Éditer un planning manuellement

1. Sélectionner un jour dans le calendrier
2. Optionnel : Déselectionner des pièces
3. Cliquer sur la timeline pour créer/modifier des créneaux
4. Utiliser "Annuler" si besoin (undo)
5. Cliquer "Enregistrer" pour sauvegarder

### Modifier via IA

Voir [ai_heating_modification.md](./ai_heating_modification.md) — bouton "✦ Modifier via IA" dans le header.

### Dupliquer un planning

Voir [heating_duplication.md](./heating_duplication.md) — chat dans la sidebar droite.

---

## Composants (voir docs dédiées)

- **Timeline - Éditeur de créneaux :** [heating_timeline.md](./heating_timeline.md)
- **Calendrier et sélection :** [heating_calendar.md](./heating_calendar.md)
- **Modification via IA :** [ai_heating_modification.md](./ai_heating_modification.md)
- **Duplication via chat IA :** [heating_duplication.md](./heating_duplication.md)

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
