# Heating Duplication - Système de duplication

Panneau de duplication de plannings avec modes jour/semaine, validation et récapitulatif.

---

## Vue d'ensemble

Permet de copier le planning d'un jour (ou d'une semaine) sur une période future, avec filtrage par jour de la semaine en mode "Jours".

**Cas d'usage typique :** Dupliquer une semaine de vacances sur les prochaines vacances scolaires.

---

## Architecture

### Structure des fichiers

```
src/components/HeatingSchedulePage/Duplication/
├── DuplicationPanel.jsx                 # Orchestrateur principal
├── DuplicationModeToggle.jsx            # Toggle Jours/Semaines
├── WeekdaySelector.jsx                  # Sélecteur L-M-M-J-V-S-D
├── DuplicationDate.jsx                  # Input date
├── DuplicationSummary.jsx               # Récapitulatif
├── DuplicationApplyButton.jsx           # Bouton validation
└── utils/
    ├── duplicationDateUtils.js          # Calculs dates
    └── duplicationValidation.js         # Règles validation
```

---

## DuplicationPanel

**Fichier :** `src/components/HeatingSchedulePage/Duplication/DuplicationPanel.jsx`

### Responsabilités

- Gérer l'état du formulaire (mode, dates, jours sélectionnés)
- Valider les paramètres de duplication
- Construire le payload pour l'API
- Afficher modal de confirmation
- Déclencher la duplication via callback `onApply`

### Modes de duplication

**Mode "Jours" :**
- Duplique un seul jour source
- Permet de choisir les jours de la semaine (L, M, M, J, V, S, D)
- Exemple : Dupliquer le lundi 15/01 sur tous les lundis et mercredis du 16/01 au 31/01

**Mode "Semaines" :**
- Duplique toute la semaine source (lundi→dimanche)
- Applique sur toutes les semaines de la période
- Exemple : Dupliquer la semaine du 8-14 janvier sur les 3 semaines suivantes

### Ajustement automatique des dates

**Mode "Semaines" :**
- `startDate` : Auto-ajusté au lundi de la semaine sélectionnée
- `endDate` : Auto-ajusté au dimanche de la semaine sélectionnée

**Contraintes min/max :**
- `startDate` ≥ source_date + 1 jour (mode Jours) ou prochain lundi (mode Semaines)
- `endDate` ≥ startDate + 1 jour (Jours) ou + 6 jours (Semaines)
- `endDate` ≤ startDate + 365 jours

### Pré-remplissage intelligent

Au changement de `sourceDate` ou de `mode` :
- `startDate` est automatiquement initialisé au minimum autorisé
- Évite les erreurs de saisie utilisateur

---

## DuplicationModeToggle

**Fichier :** `src/components/HeatingSchedulePage/Duplication/DuplicationModeToggle.jsx`

Deux boutons toggle exclusifs : **Jours** | **Semaines**

---

## WeekdaySelector

**Fichier :** `src/components/HeatingSchedulePage/Duplication/WeekdaySelector.jsx`

Affichage : 7 boutons (L-M-M-J-V-S-D) avec toggle individuel.

**Visibilité :** Uniquement en mode "Jours".

---

## DuplicationDate

**Fichier :** `src/components/HeatingSchedulePage/Duplication/DuplicationDate.jsx`

Input HTML `<input type="date">` avec contraintes `min`/`max` calculées dynamiquement.

---

## DuplicationSummary

**Fichier :** `src/components/HeatingSchedulePage/Duplication/DuplicationSummary.jsx`

### Contenu du récapitulatif

**Toujours affiché :**
- Date(s) source : "Le planning du 15/01/2025" ou "La semaine du 13/01 au 19/01"
- Liste des pièces sélectionnées

**Conditionnel :**
- **Mode Jours :** "Sera dupliqué tous les : lundis, mercredis, vendredis"
- **Mode Semaines :** "Seront dupliqués chaque semaine"
- Période : "Depuis le 16/01" / "Depuis la semaine du 20/01 au 26/01"
- "Jusqu'au XX/XX" ou "Jusqu'à la semaine du XX au XX"

### Formatage des dates

Utilise `formatDate()` pour afficher DD/MM/YYYY.

En mode Semaines, utilise `getWeekRange()` pour calculer automatiquement les lundis/dimanches.

---

## Validation

**Fichier :** `src/components/HeatingSchedulePage/Duplication/utils/duplicationValidation.js`

### Règles métier (getValidationErrors)

1. Au moins une pièce sélectionnée
2. Date de début définie
3. Date de fin définie
4. Mode "Jours" : au moins un jour de semaine sélectionné
5. Date début > date source
6. Date fin > date début
7. Mode "Semaines" : date fin ≥ date début + 6 jours (semaine complète minimum)
8. Période ≤ 365 jours

### Affichage

Les erreurs sont affichées en liste sous les champs de saisie.

Le bouton "Appliquer" est désactivé tant qu'il reste des erreurs.

---

## Utils date

**Fichier :** `src/components/HeatingSchedulePage/Duplication/utils/duplicationDateUtils.js`

Fonctions utilitaires pour manipulation de dates :

- `addDays(dateStr, days)` : Ajouter/retirer des jours
- `getNextMonday(dateStr)` : Prochain lundi après la date
- `getMondayOfWeek(dateStr)` : Lundi de la semaine de la date
- `getSundayOfWeek(dateStr)` : Dimanche de la semaine de la date
- `getWeekRange(dateStr)` : Retourne { monday, sunday, mondayText, sundayText }
- `formatDate(dateStr)` : YYYY-MM-DD → DD/MM/YYYY

---

## Flux de duplication

### Étapes utilisateur

```
1. User sélectionne jour source dans le calendrier
2. User configure les options :
   - Mode (Jours/Semaines)
   - Dates de début/fin (ajustées auto en mode Semaines)
   - Jours de la semaine (si mode Jours)
3. User vérifie le récapitulatif
4. User clique "Appliquer la duplication"
5. Modal de confirmation s'affiche
6. User confirme
```

### Traitement backend

```
7. DuplicationPanel construit le payload
8. Appel duplicateHeatingPlan(payload, accessToken, refresh)
9. Backend duplique les plannings (écrase existants)
10. Retour API : { "created/updated": 12 }
11. Page rafraîchit le calendrier
```

### Payload API

```javascript
{
  type: "day" | "week",
  source_date: "2025-01-15",
  repeat_since: "2025-01-16",
  repeat_until: "2025-01-31",
  room_ids: [1, 2, 3],
  weekdays: ["monday", "wednesday", "friday"]  // Uniquement si type="day"
}
```

---

## Modal de confirmation

Utilise le composant commun `ConfirmModal` avec :
- Titre : "Confirmer la duplication"
- Message : "Cette action écrasera les plannings existants..."
- Bouton danger : "Dupliquer"

**Important :** La duplication écrase les plannings existants sans possibilité d'annulation (pas d'undo).

---

## Interaction avec RoomsSelector

Le panneau de duplication utilise `selectedRooms` passé en prop depuis la page parent.

Les pièces affichées dans le récapitulatif correspondent aux pièces cochées dans le `RoomsSelector` de la sidebar gauche.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
