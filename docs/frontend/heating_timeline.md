# Heating Timeline - Éditeur de créneaux

Éditeur graphique de créneaux horaires avec gestion automatique des chevauchements et validation temps réel.

---

## Vue d'ensemble

Interface de type "timeline" 24h permettant de créer, modifier et supprimer des créneaux de chauffage par pièce. Gère automatiquement les chevauchements et ajuste les créneaux adjacents.

**Fonctionnalités principales :**
- Création de créneaux par clic sur zone vide (calcul auto start/end)
- Modification de créneaux existants
- Suppression avec confirmation
- Résolution automatique des chevauchements
- Validation temps réel (durée minimum, cohérence de type)
- Support température (15-25°) ou on/off

---

## Architecture

### Structure des fichiers

```
src/components/HeatingSchedulePage/Timeline/
├── Timeline.jsx                         # Orchestrateur principal
├── TimelineHeader.jsx                   # Labels horaires 00H-24H
├── TimelineSaveActions.jsx              # Boutons Annuler/Enregistrer
├── RoomSlotBar.jsx                      # Ligne pièce + barre créneaux
├── SlotBar.jsx                          # Barre horizontale cliquable
├── SlotBarLabel.jsx                     # Label nom pièce
├── TimeSlot.jsx                         # Créneau individuel
├── SlotEditModal.jsx                    # Modal création/édition
└── utils/
    ├── slotCalculations.js              # Conversions temps/pourcentage
    ├── slotTypes.js                     # Types + couleurs + labels
    ├── slotValidation.js                # Règles validation
    ├── slotAutoAdjust.js                # Calcul start/end optimal
    └── slotOverlapResolver.js           # Résolution chevauchements
```

---

## Timeline

**Fichier :** `src/components/HeatingSchedulePage/Timeline/Timeline.jsx`

### Responsabilités

- Filtrer les pièces selon `selectedRoomIds`
- Gérer l'ouverture du modal (création/modification)
- Calculer les temps optimaux pour nouveaux créneaux
- Résoudre les chevauchements avant envoi à la page parent
- Bloquer les interactions si user non authentifié

### Structure visuelle

```
┌────────────────────────────────────────────────────────────┐
│ 00H    02H    04H    06H    08H    10H    12H    14H  ...  │ ← TimelineHeader
├────────────────────────────────────────────────────────────┤
│ |      |      |      |      |      |      |      |         │ ← Grille verticale
│ Salon     [████ 20°████][███ 22°███]                       │ ← RoomSlotBar
│ Chambre   [██████████ OFF ██████████]                      │
│ Bureau              [████ 21°████]                         │
└────────────────────────────────────────────────────────────┘
```

### Gestion du modal

**État local :**
```javascript
const [selectedSlot, setSelectedSlot] = useState(null);
const [selectedRoom, setSelectedRoom] = useState(null);
const [selectedSlotIndex, setSelectedSlotIndex] = useState(null);
const [isCreating, setIsCreating] = useState(false);
```

**Ouverture création :**
User clique zone vide → `handleEmptyClick(room, clickTime)`
- Calcule `{ start, end }` optimaux via `calculateOptimalSlotTimes()`
- Détermine valeur par défaut (20° ou copie type existant)
- Ouvre modal avec `isCreating = true`

**Ouverture modification :**
User clique créneau → `handleSlotClick(room, slotData, slotIndex)`
- Ouvre modal avec données existantes
- `isCreating = false`

### Résolution des chevauchements

Avant de remonter à la page parent :
```javascript
const result = resolveSlotOverlaps(updatedSlot, room.slots, slotIndex);
onSlotUpdate(roomId, slotIndex, updatedSlot, result.resolvedSlots);
```

La page parent reçoit directement les slots résolus et les applique.

---

## RoomSlotBar

**Fichier :** `src/components/HeatingSchedulePage/Timeline/RoomSlotBar.jsx`

Container d'une ligne pièce : Label + SlotBar.

Transmet les événements (clic slot, clic vide) à Timeline avec contexte pièce.

---

## SlotBar

**Fichier :** `src/components/HeatingSchedulePage/Timeline/SlotBar.jsx`

### Responsabilités

- Afficher tous les créneaux de la pièce
- Détecter les clics sur zone vide
- Calculer la position du clic en pourcentage → temps

### Détection clic vide

```javascript
handleBarClick(e) {
  if (e.target est la barre elle-même) {
    const clickX = position relative dans la barre
    const percentClick = (clickX / largeur) * 100
    const clickTime = percentToTime(percentClick)
    onEmptyClick(clickTime)
  }
}
```

---

## TimeSlot

**Fichier :** `src/components/HeatingSchedulePage/Timeline/TimeSlot.jsx`

### Affichage

Rectangle positionné avec `left` et `width` en pourcentage (calculés par `calculateSlotPosition()`).

### Styles selon type/valeur

Utilise `getSlotClass(value, styles)` :

**Type on/off :**
- `on` → Vert
- `off` → Gris

**Type température :**
- < 16° → Bleu froid
- 16-24° → Dégradé (classe `temp16` à `temp24`)
- \> 24° → Rouge chaud

### Label

Utilise `getLabel(value)` :
- on/off → "ON" / "OFF"
- température → "20°"

---

## SlotEditModal

**Fichier :** `src/components/HeatingSchedulePage/Timeline/SlotEditModal.jsx`

### Fonctionnalités

- 3 champs : Début, Fin, Valeur
- Validation temps réel à chaque changement
- Affichage des erreurs sous les champs
- Bouton "Supprimer" (uniquement en modification)

### Validation

Appelle `validateSlot()` à chaque changement :
1. Début < Fin
2. Durée minimum 30 minutes
3. Valeur valide (0-30 pour température, "on"/"off" pour on/off)
4. Cohérence de type avec autres créneaux de la pièce

**Important :** Le modal ne valide PAS les chevauchements (géré par Timeline).

### Actions

**Valider :**
- Appelle `onSave({ start, end, value })`
- Timeline résout les chevauchements puis remonte à la page parent

**Supprimer :**
- Affiche modal de confirmation
- Si confirmé : appelle `onDelete()`
- Timeline remonte `updatedSlot = null` à la page parent

---

## Calculs de position

**Fichier :** `src/components/HeatingSchedulePage/Timeline/utils/slotCalculations.js`

### Conversions temps ↔ pourcentage

**timeToPercent(timeStr)** : "HH:MM" → 0-100
- Exemple : "12:00" → 50%

**percentToTime(percent)** : 0-100 → "HH:MM"
- Exemple : 75% → "18:00"

**calculateSlotPosition(slot)** : { start, end } → { left: "X%", width: "Y%" }
- Exemple : "08:00" - "12:00" → { left: "33.33%", width: "16.67%" }

### Conversions temps ↔ minutes

**timeToMinutes(timeStr)** : "HH:MM" → minutes depuis minuit
- Exemple : "12:30" → 750

**minutesToTime(minutes)** : minutes → "HH:MM"
- Exemple : 750 → "12:30"

---

## Types et styles

**Fichier :** `src/components/HeatingSchedulePage/Timeline/utils/slotTypes.js`

### Détection de type

**getValueType(val)** : Retourne `'temp'`, `'onoff'`, ou `null`

**isOnOff(value)** : Teste si valeur = "on" ou "off"

**isTemperature(value)** : Teste si valeur est un nombre valide

### Classes CSS

**getSlotClass(value, styles)** : Retourne la classe CSS selon la valeur
- on/off → `styles.on` ou `styles.off`
- température → `styles.temp16` à `styles.temp24` (ou `tempCold`/`tempHot`)

---

## Validation

**Fichier :** `src/components/HeatingSchedulePage/Timeline/utils/slotValidation.js`

### Règles individuelles

**validateTime(start, end)** : Vérifie start < end

**validateDuration(start, end)** : Vérifie durée ≥ 30 minutes

**validateValue(val)** : Vérifie température 0-30 ou "on"/"off"

**checkTypeConsistency(value, roomSlots, slotIndex)** : Vérifie que tous les créneaux de la pièce sont du même type

### Fonction globale

**validateSlot(start, end, value, roomSlots, slotIndex)** : Retourne objet avec clés d'erreur
```javascript
{
  time: "L'heure de début doit être avant l'heure de fin",
  value: "Valeur invalide (température 0-30 ou 'on'/'off')"
}
```

**Note :** Ne valide PAS les chevauchements (gérés séparément).

---

## Auto-ajustement

**Fichier :** `src/components/HeatingSchedulePage/Timeline/utils/slotAutoAdjust.js`

### Principe

Lors d'un clic sur zone vide, calcule automatiquement le start/end optimal pour un nouveau créneau en fonction des créneaux adjacents.

### Algorithme

**findAdjacentSlots(clickTime, slots)** : Trouve le créneau avant et après le clic

**calculateOptimalSlotTimes(clickTime, slots)** : Calcule les temps optimaux
1. Si créneau avant : start = end du créneau avant + 1 minute
2. Sinon : start = 00:00
3. Si créneau après : end = start du créneau après - 1 minute
4. Sinon : end = 23:59

**Résultat :** Nouveau créneau occupe tout l'espace disponible entre les créneaux adjacents.

---

## Résolution des chevauchements

**Fichier :** `src/components/HeatingSchedulePage/Timeline/utils/slotOverlapResolver.js`

### Principe

Lors de la création/modification d'un créneau, détecte et résout automatiquement tous les chevauchements avec les créneaux existants.

### Types de chevauchement

**1. Recouvrement total :**
Nouveau créneau recouvre entièrement un créneau existant → Suppression

**2. Recouvrement partiel au début :**
Nouveau créneau commence dans un créneau existant → Ajustement de la fin du créneau existant

**3. Recouvrement partiel à la fin :**
Nouveau créneau finit dans un créneau existant → Ajustement du début du créneau existant

### Algorithme

**resolveSlotOverlaps(newSlot, existingSlots, slotIndex)** :
1. Trouve créneaux totalement recouverts → marque pour suppression
2. Trouve créneau recouvert au début → ajuste sa fin (ou supprime si < 30 min)
3. Trouve créneau recouvert à la fin → ajuste son début (ou supprime si < 30 min)
4. Reconstruit array avec ajustements/suppressions appliqués
5. Ajoute le nouveau créneau
6. Trie par heure de début

**Retour :**
```javascript
{
  resolvedSlots: [...],      // Array final trié
  removedCount: 2,           // Nombre de créneaux supprimés
  adjustedCount: 1           // Nombre de créneaux ajustés
}
```

### Cas particuliers

**Modification d'un créneau existant :**
Le créneau en cours de modification est exclu de la détection (évite conflit avec lui-même).

**Créneau devient trop court après ajustement :**
Si l'ajustement réduit un créneau à < 30 minutes, il est supprimé plutôt qu'ajusté.

---

## RoomsSelector

**Fichier :** `src/components/HeatingSchedulePage/RoomsSelector/RoomsSelector.jsx`

### Principe

Permet de filtrer les pièces affichées dans la Timeline. Les pièces décochées disparaissent de la Timeline mais restent dans le planning (elles seront sauvegardées).

### Fonctionnalités

**Bouton "Toutes les pièces" :**
- Toggle all : sélectionne/désélectionne toutes les pièces d'un coup

**Boutons individuels :**
- Checkmark ✓ si sélectionnée
- Clic pour toggle

### Impact sur la Timeline

```javascript
const filteredRooms = rooms.filter(room => selectedRoomIds.includes(room.id));
```

Seules les pièces sélectionnées sont affichées dans la Timeline.

**Important :** La sélection influence aussi le panneau de duplication (seules les pièces sélectionnées seront dupliquées).

---

## TimelineSaveActions

**Fichier :** `src/components/HeatingSchedulePage/Timeline/TimelineSaveActions.jsx`

### Boutons

**Annuler :**
- Désactivé si `canUndo = false` (pas de changements dans l'historique)
- Appelle `undo()` du hook

**Enregistrer :**
- Désactivé si `hasChanges = false` (rien à sauvegarder)
- Appelle `save()` du hook → POST backend

---

## Flux complet d'édition

### Création de créneau

```
1. User clique zone vide de SlotBar
   ↓
2. SlotBar calcule clickTime depuis position clic
   ↓
3. Timeline.handleEmptyClick()
   - Calcule { start, end } optimaux via calculateOptimalSlotTimes()
   - Détermine valeur par défaut (copie type existant ou 20°)
   - Ouvre modal en mode création
   ↓
4. User saisit/ajuste start, end, value
   - Validation temps réel
   ↓
5. User clique "Créer"
   ↓
6. SlotEditModal.onSave({ start, end, value })
   ↓
7. Timeline.handleSlotSave()
   - Résout chevauchements via resolveSlotOverlaps()
   - Remonte resolvedSlots à la page parent
   ↓
8. Page parent appelle applyChange(newPlan)
   - Pousse état actuel dans history
   - Met à jour dailyPlan
   ↓
9. Timeline re-render avec nouveau créneau
```

### Modification de créneau

```
1. User clique TimeSlot existant
   ↓
2. Timeline.handleSlotClick(room, slotData, slotIndex)
   - Ouvre modal avec données existantes
   ↓
3. User modifie start, end, ou value
   - Validation temps réel
   ↓
4. User clique "Valider"
   ↓
5. Même flux que création (étapes 6-9)
   - slotIndex fourni pour exclure le créneau en modification
```

### Suppression de créneau

```
1. User clique "Supprimer" dans le modal
   ↓
2. Modal de confirmation s'affiche
   ↓
3. User confirme
   ↓
4. SlotEditModal.onDelete()
   ↓
5. Timeline.handleSlotDelete()
   - Remonte updatedSlot = null à la page parent
   ↓
6. Page parent supprime le créneau (splice)
   - applyChange(newPlan)
   ↓
7. Timeline re-render sans le créneau
```

---

## Gestion authentification

Si `user` est `null` :
- `handleSlotClick` et `handleEmptyClick` retournent immédiatement (pas de modal)
- Message affiché : "Vous devez être connecté pour modifier ces éléments"

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
