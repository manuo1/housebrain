# Heating Duplication - Duplication via IA conversationnelle

Composant de chat pour dupliquer un planning de chauffage vers d'autres jours, en langage naturel.

---

## Vue d'ensemble

Remplace l'ancien panneau de duplication (formulaire modes jour/semaine, datepickers, sélecteur de jours) jugé trop complexe pour un usage peu fréquent. L'utilisateur décrit sa demande en langage naturel dans une zone de chat, le backend interprète via LLM, calcule un récapitulatif, et l'utilisateur confirme avant exécution.

**Cas d'usage typique :** "copie le planning de la chambre tous les mercredis jusqu'à fin septembre"

---

## Architecture

### Structure des fichiers

```
src/
├── components/HeatingSchedulePage/
│   └── DuplicationChat/
│       ├── DuplicationChat.tsx            # Composant chat
│       └── DuplicationChat.module.scss
├── services/
│   └── duplicateHeatingPlanAi.ts          # Service HTTP
└── pages/
    └── HeatingSchedulePage.tsx            # Intégration (handleDuplicationSuccess)
```

---

## DuplicationChat

**Fichier :** `src/components/HeatingSchedulePage/DuplicationChat/DuplicationChat.tsx`

### Props

```typescript
interface DuplicationChatProps {
  sourceDate: string;
  onDuplicationSuccess: () => void;
}
```

### État interne

- `echanges` : historique complet `{role: "user"|"assistant", content: string}[]`, affiché intégralement (fil de discussion, pas juste le dernier message)
- `step` : `"clarify"` (défaut, input actif) | `"to_validate"` (boutons Oui/Non) | `"error"` (bouton Recommencer) | `null` (état initial)
- `data` : dernier `{room_ids, weekdays, start, end}` renvoyé par le back — traçabilité uniquement, transmis tel quel au step `validate`
- `networkError` : erreurs réseau/HTTP locales (distinct des messages d'erreur métier qui arrivent dans `echanges` via le back)

### Rendu conditionnel selon `step`

- **`null`/`"clarify"`** : input texte + bouton Envoyer
- **`"to_validate"`** : boutons Oui/Non (input masqué)
- **`"error"`** : bouton Recommencer (reset complet de l'état)

### Comportement "Non" après récapitulatif

Ne renvoie **aucune requête réseau** : repasse simplement `step` à `"clarify"` côté front pour rouvrir l'input. L'utilisateur tape sa correction, qui part comme un envoi normal (`handleSend`) — le LLM comprend la correction depuis l'historique complet des `echanges`, pas de mécanisme dédié.

### Warning ">30 jours"

Aucune gestion spéciale côté front : le back ajoute ce message comme un message assistant standard dans `echanges` (après le recap), donc il s'affiche naturellement dans le fil, avant les boutons Oui/Non.

---

## duplicateHeatingPlanAi

**Fichier :** `src/services/duplicateHeatingPlanAi.ts`

### Signature

```typescript
export default async function duplicateHeatingPlanAi(
  sourceDate: string,
  echanges: Echange[],
  accessToken: string,
  refreshCallback: RefreshCallback,
  step: "clarify" | "validate" = "clarify",
  data?: DuplicationData | null
): Promise<AiDuplicateResponse>
```

**Endpoint :** `POST /api/ai/heating/duplicate/`

**Important :** `step` est envoyé à **chaque** appel (défaut `"clarify"`), pas seulement au moment de valider — le backend l'exige en entrée systématiquement (voir doc backend). `weekdays` dans `DuplicationData` est `number[]` (jours ISO 0-6), pas des strings.

Utilise `fetchWithAuth` (refresh token automatique en cas de 401), même pattern que `applyAiPlanModification.ts`.

---

## Intégration dans HeatingSchedulePage

**Fichier :** `src/pages/HeatingSchedulePage.tsx`

### Placement

Zone `.rightPanel` (classe SCSS conservée de l'ancien `DuplicationPanel`), affichée uniquement si `user` est connecté et qu'une date est sélectionnée.

```tsx
{user && selectedDate && (
  <div className={styles.rightPanel}>
    <DuplicationChat sourceDate={selectedDate} onDuplicationSuccess={handleDuplicationSuccess} />
  </div>
)}
```

### handleDuplicationSuccess

```typescript
const handleDuplicationSuccess = async () => {
  if (!currentMonth) return;
  try {
    const data = await fetchHeatingCalendar(currentMonth.year, currentMonth.month);
    setCalendar(data);
  } catch (error) {
    console.error("Error reloading calendar after duplication:", error);
  }
};
```

Refetch uniquement le calendrier du mois courant (les jours dupliqués peuvent changer de statut affiché — `normal`/`different`). Pas de refetch du `dailyPlan` affiché : les dates ciblées par une duplication sont toujours postérieures à `sourceDate`, jamais `sourceDate` elle-même.

### Responsive mobile

`.rightPanel` (dans `HeatingSchedulePage.module.scss`) était masqué en mobile avec l'ancien panneau (trop complexe à adapter). Reste affiché avec le chat : passe en pleine largeur, sous le contenu principal, quand `.heatingSchedulePage` bascule en `flex-direction: column` (breakpoint `lg`).

---

## Flux d'interaction

```
User tape une instruction → Envoyer
→ echanges += {role: "user", content: instruction}
→ POST /api/ai/heating/duplicate/ (step: "clarify")

  Cas "clarify" (question de précision) :
  → echanges/step/data remplacés par la réponse back
  → Message assistant affiché, input réactivé

  Cas "to_validate" (récapitulatif prêt) :
  → Message assistant (recap) affiché
  → Boutons Oui/Non affichés

    User clique "Oui" :
    → POST (step: "validate", data)
    → Succès → onDuplicationSuccess() + reset du chat
    → Erreur métier → repasse en "clarify" avec message explicatif

    User clique "Non" :
    → step repasse à "clarify" localement (pas d'appel réseau)
    → User tape sa correction → repart comme un envoi normal

  Cas "error" (garde-fou ~10 échanges sans résolution) :
  → Bouton "Recommencer" → reset complet
```

---

## Nettoyage de l'ancien mécanisme

Ancien panneau (`Duplication/DuplicationPanel.tsx` + sous-composants `DuplicationModeToggle`, `WeekdaySelector`, `DuplicationDate`, `DuplicationSummary`, `DuplicationApplyButton`, `utils/duplicationValidation.ts`) et service `duplicateHeatingPlan.ts` entièrement supprimés. Fonctions `dateUtils.ts` devenues mortes avec ce retrait également supprimées : `getDayShort`, `WEEKDAYS`, `getMondayOfWeek`, `getSundayOfWeek`, `getNextMonday`, `getWeekRange`.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
