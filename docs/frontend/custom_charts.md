# Custom Charts - Graphiques personnalisés

Composants de visualisation de données développés en CSS/HTML pur sans librairie externe.

---

## Vue d'ensemble

### Principe

Graphiques custom développés en pur CSS/HTML avec React pour éviter les dépendances externes (Chart.js, Recharts, etc.).

**Raisons du développement custom :**

1. **Distinction physique Watt vs Watt-heure**
   - Watt (W) : puissance instantanée → visualisation par ligne en créneaux
   - Watt-heure (Wh) : énergie cumulée → visualisation par aire sous la courbe
   - Besoin de combiner ou afficher séparément ces deux représentations

2. **Périodes tarifaires variables**
   - Heures Creuses / Heures Pleines / Tempo (bleu/blanc/rouge)
   - Chaque point peut avoir sa propre couleur selon la période tarifaire
   - Les libs standards ne gèrent pas nativement ce changement de couleur point par point

3. **Contrôle total**
   - Performance optimale (pas de surcharge lib)
   - Personnalisation totale (tooltips, animations, interactions)
   - Bundle size réduit

**Type de graphique :**
- **StepChart** : Graphique en créneaux avec lignes de connexion et/ou aire sous la courbe

---

## Architecture StepChart

### Structure des fichiers

```
src/components/ConsumptionBlock/StepChart/
├── StepChart.jsx                      # Composant principal
├── StepChart.module.scss
├── Axis/
│   ├── AxisX.jsx                      # Axe horizontal (labels temps)
│   ├── AxisX.module.scss
│   ├── AxisY.jsx                      # Axe vertical (labels valeurs)
│   └── AxisY.module.scss
├── GridLines/
│   ├── HorizontalGridLines.jsx        # Lignes verticales (temps)
│   ├── HorizontalGridLines.module.scss
│   ├── VerticalGridLines.jsx          # Lignes horizontales (valeurs)
│   └── VerticalGridLines.module.scss
└── DrawArea/
    ├── DrawArea.jsx                   # Container des points
    ├── DrawArea.module.scss
    └── DataPoint/
        ├── DataPoint.jsx              # Point de données
        ├── DataPoint.module.scss
        ├── AreaRectangle.jsx          # Aire sous la courbe
        ├── AreaRectangle.module.scss
        ├── LineRectangle.jsx          # Ligne en créneaux (courbe)
        ├── LineRectangle.module.scss
        ├── HoverRectangle.jsx         # Zone hover + tooltip
        └── HoverRectangle.module.scss
```

---

## Composant principal : StepChart

### Props

```javascript
data: {
  axisY: {
    labels: string[]  // Labels axe vertical (ex: ["2000W", "1500W", "1000W", "500W", "0W"])
  },
  axisX: {
    labels: string[]  // Labels axe horizontal (ex: ["00:00", "06:00", "12:00", "18:00", "24:00"])
  },
  values: DataPoint[] // Array de points de données (voir structure ci-dessous)
}
```

### Structure d'un DataPoint

```javascript
{
  area_height: number,     // Hauteur de l'aire en % (0-100)
  area_color: string,      // Couleur de remplissage (CSS color) - varie selon période tarifaire
  line_height: number,     // Hauteur de la ligne de connexion en % (peut être négative)
  line_color: string,      // Couleur de la ligne (CSS color) - varie selon période tarifaire
  tooltip: {
    title: string,         // Titre du tooltip (ex: "12:00 → 12:30")
    content: string[]      // Lignes de contenu (ex: ["450 Wh", "900 W", "0.08 €"])
  }
}
```

### Hiérarchie des composants

```
StepChart
├── AxisY (labels verticaux)
├── chartArea (zone du graphique)
│   ├── VerticalGridLines (lignes horizontales)
│   ├── HorizontalGridLines (lignes verticales)
│   └── DrawArea
│       └── DataPoint[] (1 par valeur)
│           ├── LineRectangle (courbe en créneaux)
│           ├── AreaRectangle (aire sous la courbe)
│           └── HoverRectangle (interaction)
└── AxisX (labels horizontaux)
```

---

## Layout CSS Grid

### Structure du StepChart

```scss
.stepChart {
  display: grid;
  grid-template-columns: auto 1fr;  // AxisY | chartArea
  grid-template-rows: 1fr auto;     // chartArea | AxisX
}
```

**Placement :**
- `AxisY` : colonne 1, ligne 1
- `chartArea` : colonne 2, ligne 1
- `AxisX` : colonne 2, ligne 2

---

## DataPoint - Gestion de l'espace

### Principe critique : tableau complet requis

**IMPORTANT :** Le nombre de points doit correspondre EXACTEMENT à la résolution affichée.

**Exemples :**
- Résolution 1 heure sur 24h → **24 points** obligatoires
- Résolution 30 min sur 24h → **48 points** obligatoires
- Résolution 1 min sur 24h → **1440 points** obligatoires

**Problème si points manquants :**

```javascript
// ❌ MAUVAIS - manque le point 12:30
values: [
  { tooltip: { title: "12:00 → 12:30" } },
  // TROU ICI
  { tooltip: { title: "13:00 → 13:30" } }
]
// Résultat : le point "13:00" sera affiché à la place de "12:30" !
```

**Solution :** Le backend doit toujours renvoyer un tableau complet avec données interpolées ou valeurs nulles.

### Répartition automatique de l'espace

```scss
.dataPoint {
  flex: 1;        // Division égale de l'espace entre tous les points
  min-width: 0;   // Permet réduction en-dessous de la taille du contenu
  position: relative;
  height: 100%;
}
```

**Avantage :** Le navigateur calcule automatiquement la largeur exacte de chaque point pour éviter les gaps ou overlaps, même avec 1440 points.

---

## Sous-composants DataPoint

### LineRectangle - Courbe en créneaux

**Rôle :** Dessine la ligne reliant deux points consécutifs pour former une courbe en créneaux (step curve).

**Usage :** Représentation de valeurs **instantanées** (puissance en Watts).

**Logique :**

**line_height > 0 (montée) :**
```
  |     Point suivant plus haut
  |     Ligne monte depuis le haut de la barre actuelle
 -+
  |
```

**line_height < 0 (descente) :**
```
  |
 -+     Point suivant plus bas
  |     Ligne descend depuis le haut de la barre actuelle
  |
```

**line_height = 0 (plat) :**
```
------   Ligne horizontale au sommet de la barre
  |
```

**Style dynamique :**
```scss
.lineRectangle {
  position: absolute;
  left: 0;
  right: 0;
  border: 2px solid {line_color};
  z-index: 2;
  // bottom et height calculés selon line_height
}
```

### AreaRectangle - Aire sous la courbe

**Rôle :** Zone remplie représentant l'aire sous la courbe.

**Usage :** Représentation de quantités **cumulées** (énergie en Watt-heures).

**Distinction physique :**
- **Watt (W)** : puissance instantanée → afficher uniquement LineRectangle
- **Watt-heure (Wh)** : énergie sur une période → afficher AreaRectangle (avec ou sans ligne)

**Style :**
```scss
.areaRectangle {
  position: absolute;
  bottom: 0;              // Ancré en bas
  left: 0;
  right: 0;
  height: {area_height}%; // Hauteur dynamique
  background-color: {area_color};
  opacity: 0.5;
  z-index: 1;
}
```

### Couleurs selon périodes tarifaires

**Exemple :**
```javascript
[
  { area_color: '#3b82f6', ... }, // 00:00 HC (bleu)
  { area_color: '#3b82f6', ... }, // 06:30 HC (bleu)
  { area_color: '#ef4444', ... }, // 07:00 HP (rouge)
  { area_color: '#ef4444', ... }, // 21:30 HP (rouge)
  { area_color: '#3b82f6', ... }, // 22:00 HC (bleu)
]
```

Chaque point a sa propre couleur définie par le backend selon la période tarifaire en cours.

### HoverRectangle - Interaction et tooltip

**Rôle :** Zone invisible pour détecter le hover et afficher le tooltip.

**Style :**
```scss
.hoverRectangle {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  cursor: pointer;
  background-color: transparent;

  &:hover {
    background: linear-gradient(...);
    box-shadow: inset 2px 0 0 0 rgba(...);
  }
}
```

**Tooltip positionné intelligemment :**
- Calcul de la position du point dans le graphique
- Si à gauche → tooltip à droite
- Si à droite → tooltip à gauche
- Évite le débordement hors du container

---

## Axes et labels

### AxisY - Axe vertical

**Rôle :** Labels des valeurs (puissance, consommation, coût, etc.).

**Affichage :**
- Labels inversés (du haut vers le bas)
- Alignés à droite
- Espacement automatique avec `justify-content: space-between`

### AxisX - Axe horizontal

**Rôle :** Labels temporels (heures).

**Responsive :**
```scss
// Mobile : afficher 1 label sur 4
@media (max-width: 768px) {
  .xLabel:not(:nth-child(4n + 1)) {
    display: none;
  }
}

// Tablette : afficher 1 label sur 2
@media (min-width: 768px) {
  .xLabel:not(:nth-child(2n + 1)) {
    display: none;
  }
}
```

---

## Grilles de fond

### VerticalGridLines

**Rôle :** Lignes horizontales espacées selon les labels Y.

**Génération :**
```javascript
Array.from({ length: count }, (_, index) => (
  <div key={index} className={styles.gridLine} />
))
```

**Style :**
```scss
.gridLine {
  width: 100%;
  height: 1px;
  border-top: 1px dashed $border-medium;
  opacity: 0.5;
}
```

### HorizontalGridLines

**Rôle :** Lignes verticales espacées selon les labels X.

**Style :**
```scss
.gridLine {
  width: 1px;
  height: 100%;
  border-left: 1px dashed $border-medium;
  opacity: 0.5;
}
```

---

## Gestion des données manquantes

### Fallback UI

Si `data` est `null` ou `undefined` :

```javascript
<StepChart data={null} />
```

Affiche un graphique vide avec labels "-" et grilles par défaut :
- AxisY : 5 lignes
- AxisX : 24 colonnes

---

## Performance

### Optimisations

**Nombre de points :**
- Support de N'IMPORTE QUEL nombre de points (24, 48, 1440, ...)
- Flexbox gère automatiquement la répartition
- Pas de calcul JavaScript pour les largeurs
- Testé avec 1440 points (résolution 1 min) sans problème de performance

**Rendering :**
- CSS pur pour le dessin (GPU accelerated)
- Pas de canvas manipulation
- Tooltip affiché uniquement au hover

**Z-index layers :**
```
z-index: 1  → AreaRectangle (fond)
z-index: 2  → LineRectangle (ligne)
z-index: 10 → HoverRectangle (interaction)
```

---

## Exemple d'utilisation

```javascript
import StepChart from './components/StepChart/StepChart';

const data = {
  axisY: {
    labels: ['2000 W', '1500 W', '1000 W', '500 W', '0 W']
  },
  axisX: {
    labels: ['00:00', '06:00', '12:00', '18:00', '24:00']
  },
  values: [
    {
      area_height: 45,
      area_color: '#3b82f6',    // Bleu (HC)
      line_height: 5,
      line_color: '#3b82f6',
      tooltip: {
        title: '00:00 → 00:30',
        content: ['450 Wh', '900 W moyen', '0.08 €']
      }
    },
    // ... exactement 48 points pour résolution 30 min
  ]
};

<StepChart data={data} />
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
