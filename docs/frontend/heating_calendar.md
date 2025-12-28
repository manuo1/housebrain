# Heating Calendar - Calendrier mensuel

Composant de navigation calendaire avec visualisation des états de planification.

---

## Vue d'ensemble

Calendrier mensuel permettant de naviguer entre les dates et de visualiser en un coup d'œil l'état des plannings (vide, normal, différent du template).

---

## Architecture

### Structure des fichiers

```
src/components/HeatingSchedulePage/
├── Calendar/
│   ├── HeatingCalendar.jsx              # Calendrier principal
│   ├── CalendarDay.jsx                  # Cellule jour
│   └── CalendarDay.module.scss
└── DateHeader/
    └── DateHeader.jsx                   # En-tête date formatée
```

---

## HeatingCalendar

**Fichier :** `src/components/HeatingSchedulePage/Calendar/HeatingCalendar.jsx`

### Responsabilités

- Afficher la grille mensuelle (semaines complètes avec jours hors mois)
- Gérer la navigation précédent/suivant avec transition année
- Transmettre la sélection de jour à la page parent

### Fonctionnement

**Navigation :**
Boutons `◀` / `▶` déclenchent `onMonthChange(year, month)`.

**Affichage :**
Grille 7 colonnes (L-M-M-J-V-S-D) organisée par semaines. Les jours du mois précédent/suivant sont affichés en grisé.

---

## CalendarDay

**Fichier :** `src/components/HeatingSchedulePage/Calendar/CalendarDay.jsx`

### États visuels

Chaque jour affiche son numéro avec des styles conditionnels selon :

**États de planification :**
- `empty` : Pas de planning défini (style discret)
- `normal` : Planning identique au même jour de la semaine précédente (style par défaut)
- `different` : Planning différent de la semaine précédente (pastille rouge distinctive)

**Utilité du statut "different" :**
Met en évidence les semaines atypiques (vacances, jours fériés) qui ont un planning spécifique. Facilite la navigation pour retrouver une semaine de vacances précédente à dupliquer sur une nouvelle période de vacances.

**États contextuels :**
- `otherMonth` : Jour hors mois courant (grisé)
- `today` : Aujourd'hui (bordure spéciale)
- `selected` : Jour sélectionné (surbrillance)

### Interaction

Bouton cliquable qui remonte `dateISO` via `onClick` → déclenche le fetch du planning dans la page parent.

---

## DateHeader

**Fichier :** `src/components/HeatingSchedulePage/DateHeader/DateHeader.jsx`

Composant d'affichage simple qui formate un `SimpleDate` en : **"Lundi 08/12/2025"**

Utilise `formatFullDayLabel()` depuis `dateUtils.js`.

---

## Flux d'interaction

### Sélection de date

```
User clique jour → CalendarDay.onClick()
→ HeatingCalendar.onDateSelect(dateISO)
→ Page change selectedDate
→ Hook useHeatingPlanHistory refetch automatique
```

### Changement de mois

```
User clique ◀/▶ → HeatingCalendar calcule year/month
→ onMonthChange(year, month)
→ Page met à jour currentMonth
→ useEffect refetch calendrier
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
