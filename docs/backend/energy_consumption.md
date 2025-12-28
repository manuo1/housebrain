# Monitoring consommation électrique

Système d'historisation et d'analyse de la consommation électrique avec résolution à la minute.

---

## Vue d'ensemble

Le module consumption collecte et stocke les index énergétiques du compteur Linky minute par minute. Il permet l'analyse de la consommation avec plusieurs résolutions temporelles et le calcul automatique des coûts selon les tarifs EDF.

---

## Collecte des données

### Fréquence
La collecte est déclenchée par le scheduler toutes les 1 minute.

### Source des données
Les index énergétiques sont lus depuis le cache Redis alimenté par le listener Téléinfo.

### Données collectées
- Index énergétiques par label (HCHC, HCHP, BASE, etc.)
- Période tarifaire en cours (HC, HP, HCJB, etc.)
- Puissance souscrite (kVA)

### Gestion de minuit
À 00:00, le système enregistre les données à la fois pour :
- 00:00 du jour actuel
- 24:00 du jour précédent (continuité des séries temporelles)

---

## Stockage

### Modèle DailyIndexes

```python
date              # Date unique (clé primaire)
values            # JSON: {HCHC: {00:00: 12345, 00:01: 12346, ...}}
tarif_periods     # JSON: {00:00: "HC..", 00:01: "HC..", ...}
subscribed_power  # Float: puissance souscrite en kVA
```

### Structure des index

Les index sont stockés par minute (1440 points par jour) :

```json
{
  "HCHC": {
    "00:00": 12345678,
    "00:01": 12345680,
    "00:02": null,
    ...
  },
  "HCHP": {
    "00:00": 23456789,
    ...
  }
}
```

---

## Traitement des données

### Interpolation linéaire

Les valeurs manquantes (null) sont interpolées automatiquement en utilisant les valeurs encadrantes.

**Algorithme :**
1. Détection des zones de valeurs manquantes encadrées par des valeurs connues
2. Calcul de la différence totale entre début et fin
3. Distribution équitable avec gestion du reste (évite erreurs d'arrondi)

**Exemple :**
```
10:00 = 1000 Wh
10:01 = null
10:02 = null
10:03 = 1006 Wh

→ Différence = 6 Wh sur 3 intervalles
→ 10:01 = 1002 Wh
→ 10:02 = 1004 Wh
```

### Multi-résolution

Les données peuvent être agrégées selon 3 résolutions :

| Step | Points par jour | Usage |
|------|----------------|-------|
| 1 min | 1440 | Analyse détaillée, interpolation |
| 30 min | 48 | Visualisation journée complète |
| 60 min | 24 | Vue d'ensemble, export |

Le downsampling conserve uniquement les points alignés sur le step (00:00, 00:30, 01:00...).

### Calcul de consommation

La consommation en watt-heures (Wh) est calculée par différence entre index consécutifs :

```
Wh[00:00→00:01] = Index[00:01] - Index[00:00]
```

La puissance moyenne (W) est déduite du Wh et du step :

```
W_moyen = Wh / (step / 60)
```

---

## Tarification EDF

### Pricing historique

Le système gère l'évolution des tarifs EDF dans le temps via `edf_pricing.py`.

Les tarifs sont stockés par date d'application et période tarifaire :

```python
pricing = {
    date(2025, 2, 1): {
        "kwh": {
            TarifPeriods.HC: 16.96,  # centimes
            TarifPeriods.HP: 21.46,
            ...
        }
    }
}
```

### Calcul du coût

Pour chaque intervalle de consommation :

```
Coût (€) = (Wh / 1000) × Prix_kWh(date, période_tarifaire)
```

Le prix appliqué est celui en vigueur à la date de consommation.

### Totaux journaliers

Les totaux sont calculés par période tarifaire :

```json
{
  "Heures Creuses": {"wh": 5420, "euros": 0.92},
  "Heures Pleines": {"wh": 3180, "euros": 0.68},
  "Total": {"wh": 8600, "euros": 1.60}
}
```

---

## API REST

### Endpoint principal

```
GET /api/consumption/daily/?date=YYYY-MM-DD&step=1
```

**Paramètres :**
- `date` (requis) : Date de consommation (YYYY-MM-DD)
- `step` (optionnel) : Résolution en minutes (1, 30 ou 60, défaut : 1)

**Réponse :**

```json
{
  "date": "2025-12-27",
  "step": 30,
  "data": [
    {
      "date": "2025-12-27",
      "start_time": "00:00",
      "end_time": "00:30",
      "wh": 450,
      "average_watt": 900,
      "euros": 0.076,
      "interpolated": false,
      "tarif_period": "Heures Creuses"
    },
    ...
  ],
  "totals": {
    "Heures Creuses": {"wh": 5420, "euros": 0.92},
    "Heures Pleines": {"wh": 3180, "euros": 0.68},
    "Total": {"wh": 8600, "euros": 1.60}
  }
}
```

### Endpoint index bruts

```
GET /backend/consumption/indexes/YYYY-MM-DD/
```

Retourne les index bruts (JSON) sans traitement.

---

## Gestion des périodes tarifaires

### Mapping bidirectionnel

Le système maintient un mapping entre :
- Labels d'index Téléinfo (HCHC, HCHP, BBRHCJB...)
- Labels de période tarifaire (HC.., HP.., HCJB...)
- Labels lisibles ("Heures Creuses", "Heures Pleines Jours Bleus"...)

### Correction automatique

Les changements de période tarifaire se produisent toujours à l'heure pile (07:00, 22:00...).

En cas de délai de lecture Téléinfo, si le changement est détecté à 07:01 alors que 07:00 contient encore l'ancienne période, le système corrige automatiquement 07:00.

---

## Consultation

### Interface admin

```
/backend/admin/consumption/dailyindexes/
```

Liste des jours avec données stockées. Les données JSON sont consultables mais non modifiables.

---

## Limites et contraintes

### Données manquantes

Si trop de données sont manquantes (trous > quelques minutes), l'interpolation peut être inexacte. Le flag `interpolated: true` indique les valeurs reconstruites.

### Changement d'heure

Le système ne gère pas automatiquement les passages heure d'été/hiver. Les jours de 23h ou 25h nécessitent un traitement manuel si besoin.

### Rétention

Les données sont conservées indéfiniment. Aucune purge automatique n'est configurée.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
