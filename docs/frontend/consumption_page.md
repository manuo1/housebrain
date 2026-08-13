# Consumption Page - Analyse de consommation

Page d'analyse de la consommation électrique avec graphiques personnalisés et totaux par période tarifaire.

---

## Vue d'ensemble

Visualisation des données de consommation électrique journalière avec possibilité de comparer deux jours côte à côte.

**Route :** `/consumption`

**Fonctionnalités :**
- Graphiques de consommation en plusieurs résolutions (1 min, 30 min, 1h)
- Affichage en Wh, Watts moyens, ou Euros
- Totaux par période tarifaire (HC/HP, Tempo, etc.)
- Comparaison de deux jours différents

---

## Architecture

### Structure des fichiers

```
src/
├── pages/
│   └── ConsumptionPage.tsx              # Page principale (2 blocs), export DailyConsumptionPage
├── components/
│   └── ConsumptionBlock/
│       ├── ConsumptionBlock.tsx         # Bloc graphique complet
│       ├── FilterBar/
│       │   ├── FilterBar.tsx            # Barre de filtres
│       │   ├── TypeSelector.tsx         # Sélecteur Wh/W/€
│       │   ├── TimeStepSelector.tsx     # Sélecteur résolution
│       │   └── DateSelector.tsx         # Sélecteur date
│       ├── StepChart/                   # Graphique custom (voir doc dédiée)
│       │   ├── StepChart.tsx
│       │   ├── Axis/                    # AxisX, AxisY
│       │   ├── GridLines/               # VerticalGridLines, HorizontalGridLines
│       │   └── DrawArea/
│       │       └── DataPoint/           # AreaRectangle, LineRectangle, HoverRectangle, DataPoint
│       └── TotalsCards/
│           ├── TotalsCards.tsx          # Container des totaux
│           └── TotalCard.tsx            # Carte individuelle
├── constants/
│   └── consumptionConstants.ts          # VALUE_TYPES (wh/average_watt/euros), STEP_OPTIONS (1/30/60)
├── services/
│   └── fetchDailyConsumption.ts         # Appel API
├── transformers/
│   └── consumptionToChart/              # Logique de transformation
│       ├── consumptionToChart.ts        # Orchestrateur principal
│       ├── computeAxisX.ts              # Labels heures
│       ├── computeAxisY.ts              # Labels valeurs + max
│       ├── computeChartValues.ts        # Transformation points
│       ├── computeAreaHeight.ts         # Hauteur barre (%)
│       ├── computePointColors.ts        # Couleurs périodes tarifaires
│       ├── computeLineHeight.ts         # Delta point suivant
│       ├── computeTooltip.ts            # Contenu tooltip
│       └── constants.ts                 # Couleurs + config
└── models/
    └── DailyConsumption.ts              # Modèle de données (typé)
```

---

## Page ConsumptionPage

**Fichier :** `src/pages/ConsumptionPage.tsx` (export `DailyConsumptionPage`)

### Structure

```tsx
<div className={styles.dailyConsumption}>
  <div className={styles.graphBlock}>
    <ConsumptionBlock />
  </div>
  <div className={styles.graphBlock}>
    <ConsumptionBlock />
  </div>
</div>
```

**Principe :** 2 blocs indépendants pour comparer facilement deux jours différents.

---

## Composant ConsumptionBlock

**Fichier :** `src/components/ConsumptionBlock/ConsumptionBlock.tsx`

### État local

```typescript
const [date, setDate] = useState<string>(getTodayDate()); // dateUtils, évite le bug UTC (veille entre 0h-2h)
const [step, setStep] = useState<number>(1);              // 1, 30, ou 60 minutes
const [displayType, setDisplayType] = useState<DisplayType>('average_watt'); // 'wh', 'average_watt', ou 'euros'
const [dailyConsumption, setDailyConsumption] = useState<DailyConsumption | null>(null);
const [isLoading, setIsLoading] = useState<boolean>(true);
const [error, setError] = useState<string | null>(null);
```

### Flux de données

```
1. Changement date/step
   ↓
2. useEffect déclenche fetchDailyConsumption()
   ↓
3. Données stockées dans dailyConsumption
   ↓
4. useMemo transforme avec transformDailyConsumptionToChart()
   ↓
5. chartData passé au StepChart
```

### Rendu

```jsx
<div className={styles.consumptionBlock}>
  <FilterBar {...} />
  <StepChart data={chartData} isLoading={isLoading} />
  <TotalsCards totals={dailyConsumption?.totals} />
  {/* Overlay loading/error */}
</div>
```

`StepChart` reçoit `isLoading` pour appliquer une classe `.loading` (opacity) pendant le fetch, sans démonter le graphique — évite le flash graph→vide→graph lors de la nav jour/jour.

---

## FilterBar

**Fichier :** `src/components/ConsumptionBlock/FilterBar/FilterBar.tsx`

### Sous-composants

**TypeSelector :**
- Boutons : Consommation (Wh) / Puissance Moyenne (W) / Coût (€)
- Change le type d'affichage sans refetch

**DateSelector :**
- Input date natif
- Boutons précédent/suivant
- Max = aujourd'hui (pas de dates futures)

**TimeStepSelector :**
- Boutons : 1 min / 30 min / 1 h
- Change la résolution et refetch les données

### Responsive

Layout flex qui passe en colonne sur mobile :
```scss
@media (max-width: 1024px) {
  .filterBar {
    flex-direction: column;
  }
}
```

---

## Transformers - Logique métier

### consumptionToChart.js

**Rôle :** Orchestrateur principal qui transforme les données backend en format graphique.

```javascript
transformDailyConsumptionToChart(dailyConsumption, displayType)
```

**Étapes :**
1. Génère labels axe X (heures)
2. Calcule labels axe Y + max (nice numbers)
3. Transforme chaque point avec computeChartValues()

### computeAxisX.js

**Rôle :** Génère les labels horaires selon le step.

**Sortie :**
```javascript
['00:00', '01:00', '02:00', ..., '24:00']
```

### computeAxisY.js

**Rôle :** Calcule les graduations de l'axe Y avec "nice numbers".

**Algorithme :**
1. Trouve le max des données
2. Arrondit à un "nice number" (ex: 2347 → 2500)
3. Trouve un step joli (ex: 500)
4. Ajuste le max pour être un multiple du step
5. Génère les labels réguliers

**Sortie exemple :**
```javascript
{
  labels: ['0 Wh', '500 Wh', '1000 Wh', '1500 Wh', '2000 Wh'],
  max: 2000
}
```

### computeChartValues.js

**Rôle :** Transforme chaque point de données en format graphique.

**Pour chaque point :**
1. `computeAreaHeight()` → hauteur barre en %
2. `computePointColors()` → couleurs selon période tarifaire
3. `computeLineHeight()` → delta avec point suivant
4. `computeTooltip()` → contenu du tooltip

**Sortie :**
```javascript
{
  area_height: 45,
  area_color: '#3b82f6',
  line_height: 5,
  line_color: '#3b82f6',
  tooltip: {
    title: '00:00 → 00:30',
    content: ['450 Wh', '900 W', '0.08 €', 'Heures Creuses', '⚠️ Donnée interpolée']
  }
}
```

---

## Gestion des couleurs

### constants.js - TARIF_PERIOD_COLORS

**Principe :** Palette de couleurs réutilisable par groupe tarifaire.

**Groupes mutuellement exclusifs :**

```javascript
// Groupe 1 : Tarif unique
'Toutes les Heures': '#3b82f6'

// Groupe 2 : EJP
'Heures Normales': '#3b82f6'
'Heures de Pointe Mobile': '#ef4444'

// Groupe 3 : HC/HP classique
'Heures Creuses': '#10b981'
'Heures Pleines': '#f59e0b'

// Groupe 4 : Tempo (6 périodes)
'Heures Creuses Jours Bleus': '#06b6d4'
'Heures Pleines Jours Bleus': '#3b82f6'
'Heures Creuses Jours Blancs': '#a855f7'
'Heures Pleines Jours Blancs': '#8b5cf6'
'Heures Creuses Jours Rouges': '#f97316'
'Heures Pleines Jours Rouges': '#ef4444'
```

### computePointColors.js

**Logique :**

**Si valeur null :**
```javascript
{ area_color: 'transparent', line_color: 'transparent' }
```

**Si displayType === 'average_watt' (Watts) :**
```javascript
{ area_color: 'transparent', line_color: color }
// Ligne seulement, pas de remplissage
```

**Si displayType === 'wh' ou 'euros' :**
```javascript
{ area_color: color, line_color: color }
// Aire sous la courbe remplie
```

---

## TotalsCards

**Fichier :** `src/components/ConsumptionBlock/TotalsCards/TotalsCards.tsx`

### Structure des totaux

**Format backend :**
```javascript
{
  "Heures Creuses": { wh: 5420, euros: 0.92 },
  "Heures Pleines": { wh: 3180, euros: 0.68 },
  "Total": { wh: 8600, euros: 1.60 }
}
```

### Affichage

Si `totals` est absent/vide : `"Aucun total disponible"`.

Sinon, itération sur les entrées du dictionnaire, avec fallback `"-"` par valeur nulle :

```jsx
{Object.entries(totals).map(([label, total]) => (
  <TotalCard
    key={label}
    label={label}
    kwh={total?.wh != null ? formatWh(total.wh) : "-"}
    euros={total?.euros != null ? formatEuro(total.euros) : "-"}
  />
))}
```

**TotalCard :**
```
[Heures Creuses :] [5.42 kWh] [/] [0.92 €]
```

### Responsive

Layout flex qui passe en colonne sur mobile (même comportement que FilterBar).

---

## Gestion des erreurs et loading

### Overlay

**États :**
- `isLoading` : affiche spinner
- `error` : affiche message d'erreur

**Affichage :**
```jsx
{(isLoading || error) && (
  <div className={styles.overlay}>
    {isLoading && <div className={styles.spinner}></div>}
    {error && (
      <div className={styles.error}>
        <div className={styles.errorIcon}>⚠️</div>
        <div className={styles.errorMessage}>Un problème est survenu</div>
      </div>
    )}
  </div>
)}
```

### Comportement

**Pendant le chargement :**
- Overlay affiché par-dessus le graphique
- Données précédentes restent visibles (si existantes)

**En cas d'erreur :**
- Overlay avec message d'erreur
- Graphique affiche le fallback (grille vide avec labels "-")

---

## Service fetchDailyConsumption

**Fichier :** `src/services/fetchDailyConsumption.ts`

### Appel API

```javascript
GET /api/consumption/daily/?date=YYYY-MM-DD&step=1
```

**Paramètres :**
- `date` : Date au format ISO (YYYY-MM-DD)
- `step` : Résolution en minutes (1, 30, ou 60)

**Retour :**
Instance de `DailyConsumption` avec :
- `date` : Date des données
- `step` : Résolution utilisée
- `data` : Array de points (structure backend)
- `totals` : Totaux par période tarifaire

---

## Graphique StepChart

Voir documentation dédiée : [Custom Charts](./custom_charts.md)

**Points clés :**
- Graphique en créneaux (step chart)
- Distinction ligne (W) vs aire (Wh/€)
- Couleurs dynamiques par période tarifaire
- Tooltip complet avec toutes les infos

---

## Cas d'usage

### Comparer deux jours

1. Page affiche 2 blocs
2. Bloc 1 : hier
3. Bloc 2 : aujourd'hui
4. Chaque bloc peut être configuré indépendamment

### Analyser en détail

1. Sélectionner résolution 1 min
2. Voir les pics de consommation minute par minute
3. Identifier les périodes de forte consommation
4. Comparer le coût selon les périodes tarifaires

### Surveiller les coûts

1. Sélectionner affichage "Coût (€)"
2. Visualiser directement l'impact financier
3. Comparer HC vs HP
4. Optimiser les plages d'utilisation

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
