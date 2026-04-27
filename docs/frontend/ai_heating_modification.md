# AI Heating Modification - Frontend

Composant de saisie et service de modification des plannings de chauffage via IA.

---

## Vue d'ensemble

Un bouton "✦ Modifier via IA" dans le header de la page de planning ouvre une zone de saisie en slide-down. L'utilisateur tape une instruction en langage naturel, la soumet, et le plan modifié est inséré dans l'historique d'annulation exactement comme une modification manuelle.

---

## Architecture

### Structure des fichiers

```
src/
├── components/HeatingSchedulePage/
│   └── AiPlanInput/
│       ├── AiPlanInput.tsx              # Composant de saisie
│       └── AiPlanInput.module.scss      # Styles
├── services/
│   └── applyAiPlanModification.ts       # Service HTTP
└── pages/
    └── HeatingSchedulePage.tsx          # Intégration (handleAiRequest)
```

---

## AiPlanInput

**Fichier :** `src/components/HeatingSchedulePage/AiPlanInput/AiPlanInput.tsx`

### Responsabilités

- Afficher/masquer la zone de saisie (slide-down CSS)
- Gérer les états : idle, loading, erreur
- Transmettre l'instruction via `onSubmit`
- Afficher le feedback utilisateur

### Props

```typescript
interface AiPlanInputProps {
  onSubmit: (instruction: string) => Promise<void>;
  disabled?: boolean;
}
```

### États visuels

**Idle :**
Bouton "✦ Modifier via IA" visible, zone de texte masquée.

**Expanded :**
Zone de texte visible en slide-down, bouton "Appliquer" actif.

**Loading :**
Textarea désactivée, bouton affiche "Réflexion...", zone reste ouverte, instruction conservée.

**Succès :**
Zone se referme, instruction vidée.

**Erreur :**
Zone reste ouverte, instruction conservée, bordure textarea en rouge, message d'erreur affiché sous la textarea, bouton réactivé pour réessayer. Modifier le texte efface l'erreur.

### Interactions clavier

- `Entrée` : soumet l'instruction
- `Shift+Entrée` : saut de ligne
- `Échap` : ferme la zone

### Placement

Ligne 2 du header de `HeatingSchedulePage`, sous la ligne date + boutons Annuler/Enregistrer. Visible uniquement si l'utilisateur est connecté.

---

## applyAiPlanModification

**Fichier :** `src/services/applyAiPlanModification.ts`

### Responsabilités

- Envoyer l'instruction et le plan courant au backend
- Retourner un `DailyHeatingPlan` instancié
- Gérer les erreurs HTTP avec message lisible

### Signature

```typescript
export default async function applyAiPlanModification(
  payload: AiModifyPayload,
  accessToken: string,
  refreshCallback: RefreshCallback
): Promise<DailyHeatingPlan>
```

### Payload envoyé

```typescript
interface AiModifyPayload {
  instruction: string;  // Instruction en langage naturel
  plan: object;         // dailyPlan.raw — plan courant avec modifications non sauvegardées
}
```

**Important :** `plan` contient le plan tel qu'affiché à l'écran, incluant les éventuelles modifications manuelles non encore sauvegardées. Le LLM travaille donc toujours sur l'état le plus à jour.

### Gestion des erreurs

Les erreurs backend (400) remontent via `throw new Error(message)` et sont catchées par `AiPlanInput` qui les affiche sous la textarea.

### Mock

```typescript
const USE_MOCK = false; // Passer à true pour tester sans backend
```

En mode mock, retourne `mockDailyHeatingPlan` sans appel HTTP.

---

## Intégration dans HeatingSchedulePage

**Fichier :** `src/pages/HeatingSchedulePage.tsx`

### handleAiRequest

```typescript
const handleAiRequest = async (instruction: string) => {
  if (!dailyPlan || !accessToken) return;
  const newPlan = await applyAiPlanModification(
    { instruction, plan: dailyPlan.raw },
    accessToken,
    refresh
  );
  applyChange(newPlan);
};
```

Le plan retourné est passé à `applyChange()` — même chemin que toute modification manuelle → inséré dans la pile undo.

### Placement dans le JSX

```tsx
<div className={styles.header}>
  <div className={styles.headerTop}>
    <DateHeader date={selectedDateObj} />
    <TimelineSaveActions ... />
  </div>
  {user && <AiPlanInput onSubmit={handleAiRequest} />}
</div>
```

---

## Flux d'interaction

```
User clique "✦ Modifier via IA"
→ Zone de texte s'ouvre (slide-down)
→ User tape instruction
→ User clique "Appliquer" (ou Entrée)
→ Bouton passe à "Réflexion..."
→ applyAiPlanModification(instruction, dailyPlan.raw)
→ POST /api/ai/heating/modify/

  Cas succès :
  → new DailyHeatingPlan(rawData)
  → applyChange(newPlan)
  → Timeline mise à jour
  → Zone se referme

  Cas erreur :
  → throw new Error(message backend)
  → Message affiché sous textarea en rouge
  → Zone reste ouverte pour correction
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Avril 2026
