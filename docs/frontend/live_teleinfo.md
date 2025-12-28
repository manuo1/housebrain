# Live Téléinfo - Frontend

Affichage temps-réel des données du compteur Linky.

---

## Vue d'ensemble

Page de monitoring temps-réel affichant les données brutes du compteur électrique transmises par le backend via l'API Téléinfo.

**Route :** `/teleinfo`

**Rafraîchissement :** Toutes les 1 seconde

---

## Architecture

### Structure des fichiers

```
src/
├── pages/
│   └── LiveTeleinfoPage.jsx        # Page principale
├── components/
│   └── TeleinfoTable/
│       ├── TeleinfoTable.jsx       # Tableau d'affichage
│       └── TeleinfoTable.module.scss
├── services/
│   └── fetchTeleinfoData.js        # Appel API
├── models/
│   └── TeleinfoData.js             # Modèle de données
└── utils/
    └── teleinfoUtils.js            # Formatage des valeurs
```

---

## Page LiveTeleinfoPage

**Fichier :** `src/pages/LiveTeleinfoPage.jsx`

### Fonctionnement

**État local :**
- `data` : Données Téléinfo (instance de TeleinfoData)
- `error` : Message d'erreur si échec

**useEffect :**
- Fetch initial au montage
- Polling toutes les 1000ms
- Cleanup : clear interval + flag `isMounted`

**Rendu conditionnel :**
```javascript
error        → Affiche message d'erreur
!data        → Affiche "Loading data..."
data         → Affiche <TeleinfoTable />
```

---

## Service fetchTeleinfoData

**Fichier :** `src/services/fetchTeleinfoData.js`

### Appel API

**Endpoint :**
```
GET /api/teleinfo/data/
```

**Traitement :**
1. Appelle `fetchJson()` (wrapper fetch basique)
2. Instancie `TeleinfoData` avec les données brutes
3. Retourne l'instance

**Mode mock :**
```javascript
const USE_MOCK = false; // true pour dev sans backend
```

---

## Modèle TeleinfoData

**Fichier :** `src/models/TeleinfoData.js`

### Principe

Classe qui encapsule et enrichit les données brutes du backend.

### Propriétés importantes

**Données brutes parsées :**
- `OPTARIF` : Option tarifaire (string)
- `ISOUSC` : Intensité souscrite (int)
- `PTEC` : Période tarifaire en cours (string)
- `IINST` : Intensité instantanée (int)
- `IMAX` : Intensité maximale (int)
- `PAPP` : Puissance apparente (int)
- `last_read` : Timestamp dernier relevé (formaté)

**Valeurs calculées :**
- `maxPower` : Puissance max en watts (ISOUSC * 230V)
- `currentPower` : Puissance actuelle (= PAPP)
- `OPTARIFLabel` : Label lisible de l'option tarifaire
- `PTECLabel` : Label lisible de la période tarifaire

**Autres données :**
- `otherData` : Dictionnaire contenant tous les autres champs (index énergétiques, etc.)

### Constantes utilisées

**IMPORTANT_KEYS :**
Liste des champs traités en priorité (OPTARIF, ISOUSC, PTEC, IINST, IMAX, PAPP, last_read).

**Mapping labels :**
- `OPTARIF_LABELS` : "HC.." → "Heures Pleines/Creuses"
- `PTEC_LABELS` : "HC.." → "Heures Creuses"

---

## Composant TeleinfoTable

**Fichier :** `src/components/TeleinfoTable/TeleinfoTable.jsx`

### Props

```javascript
data: TeleinfoData  // Instance du modèle
```

### Affichage

Tableau HTML à 2 colonnes (Label | Valeur).

**Ordre d'affichage :**
1. Option tarifaire
2. Intensité souscrite
3. Période tarifaire en cours
4. Intensité instantanée
5. Intensité maximale
6. Puissance apparente
7. Dernier relevé
8. Autres données (index énergétiques)

**Formatage :**
Utilise `formatValue()` et `formatOtherData()` pour ajouter les unités (A, VA, Wh).

---

## Utilitaires

### formatValue(key, value)

**Fichier :** `src/utils/teleinfoUtils.js`

Ajoute l'unité appropriée selon la clé (A, VA, Wh).

### formatOtherData(otherData)

Formate les index énergétiques avec leurs labels et unités.

**Exemple :**
```javascript
{
  HCHC: "12345678"
}
→
{
  "Index Heures Creuses": "12345678 Wh"
}
```

---

## Gestion des erreurs

**Cas d'erreur :**
- Backend non disponible
- Timeout réseau
- Données manquantes/invalides

**Affichage :**
```html
<p className={styles.error}>Error: {errorMessage}</p>
```

**Comportement :**
Le polling continue malgré l'erreur (retry automatique toutes les secondes).

---

## Performance

### Optimisations

**Flag isMounted :**
Évite les setState sur composant démonté.

**Cleanup interval :**
Clear l'interval au démontage pour éviter les fuites mémoire.

### Fréquence de rafraîchissement

**1 seconde** : Compromis entre réactivité et charge serveur.

Les données Téléinfo changent en temps réel (intensité, puissance), un rafraîchissement rapide est nécessaire.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
