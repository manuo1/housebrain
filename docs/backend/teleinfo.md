# Téléinfo - Lecture compteur Linky

Système de lecture temps-réel des données du compteur électrique Linky via le protocole Téléinfo.

---

## Vue d'ensemble

Le module Téléinfo est un composant critique de HouseBrain : il constitue la base de toute la gestion et du monitoring électrique de l'application.

Il lit en continu les données transmises par le compteur Linky via le protocole série Téléinfo. Les données sont parsées, validées puis stockées dans Redis pour utilisation par tous les autres modules (consommation, chauffage, monitoring).

Sans ce listener, l'application ne peut ni :
- Calculer la consommation énergétique
- Gérer la puissance disponible
- Piloter intelligemment les radiateurs
- Détecter les risques de dépassement

---

## Protocole Téléinfo

### Communication série

**Configuration port série :**
- Port : `/dev/ttyS0` (configurable via `.env`)
- Baudrate : 1200 bauds
- Parité : None
- Stop bits : 1
- Data bits : 7
- Timeout : 1 seconde

### Format des trames

Les données sont transmises par trames ASCII contenant des étiquettes (labels) avec leurs valeurs.

**Structure d'une ligne :**
```
<LABEL> <VALEUR> <CHECKSUM>\r\n
```

Exemple :
```
ADCO 021728123456 @
IINST 004 [
PAPP 00850 .
```

### Validation checksum

Chaque ligne contient un checksum calculé sur l'ensemble `LABEL + ESPACE + VALEUR`.

**Algorithme :**
1. Somme des codes ASCII de tous les caractères
2. Conservation des 6 bits de poids faible (`somme & 0x3F`)
3. Ajout de `0x20` (caractère espace)

Le résultat est un caractère ASCII imprimable entre `0x20` et `0x5F`.

### Labels principaux

| Label | Description |
|-------|-------------|
| ADCO | Adresse du compteur |
| OPTARIF | Option tarifaire (Base, HC/HP, Tempo, EJP) |
| ISOUSC | Intensité souscrite (ampères) |
| IINST | Intensité instantanée (ampères) |
| PAPP | Puissance apparente (VA) |
| BASE / HCHC / HCHP | Index énergétiques selon option tarifaire |
| PTEC | Période tarifaire en cours |

---

## Architecture

### Service systemd dédié

Le listener fonctionne comme un service systemd indépendant avec watchdog.

**Composants :**
- `teleinfo-listener.service` : Service systemd
- `listener.py` : Boucle de lecture série
- `services.py` : Parsing et validation

**Watchdog :**
Le listener notifie systemd à chaque trame complète reçue (watchdog 15 secondes).

### Commande Django
```bash
python manage.py run_teleinfo_listener
```

---

## Parsing et validation

### Flux de traitement

1. **Lecture série :** Lecture ligne par ligne du port série
2. **Nettoyage :** Suppression caractères de contrôle (`\r`, `\n`, `\x02`, `\x03`)
3. **Split :** Extraction `LABEL`, `VALEUR`, `CHECKSUM`
4. **Validation :** Vérification du checksum calculé vs reçu
5. **Buffer :** Accumulation des lignes valides
6. **Trame complète :** Détection de toutes les étiquettes obligatoires
7. **Cache :** Stockage dans Redis

### Buffer et trame complète

Le buffer accumule les données jusqu'à avoir toutes les étiquettes obligatoires :
- `ADCO` (marqueur début de trame)
- `MOTDETAT`
- `IINST`
- `ISOUSC`
- `PAPP`

Une fois complète, la trame est copiée dans le cache puis le buffer est vidé.

---

## Stockage cache

### Redis
Les données Téléinfo sont stockées dans Redis avec :
- Clé : `teleinfo_data`
- Timeout : `None` (persistant)
- Structure : dictionnaire avec timestamp `last_read`

### Fraîcheur des données
Les données sont considérées valides si `last_read` date de moins de 5 secondes.

---

## Gestion de la puissance

Le listener intègre également la gestion temps-réel de la puissance disponible. Bien que cela crée un couplage entre les composants, cette architecture est nécessaire car :

- Le listener est le seul à connaître la puissance disponible instantanée (données compteur)
- La réactivité est critique : tout délai pourrait causer un dépassement de puissance souscrite
- Les dépassements entraînent des coupures ou surcoûts EDF

Le listener appelle donc directement les fonctions de délestage et d'allumage des radiateurs à chaque trame complète.

---

## Monitoring

### Page de monitoring
```
/backend/teleinfo/data/
```

Affiche toutes les données Téléinfo en temps-réel (auto-refresh recommandé).

### API REST
```
/api/teleinfo/
```

Endpoints REST pour accès programmatique aux données Téléinfo.

### Logs
```bash
# Logs temps-réel
sudo journalctl -u teleinfo-listener -f

# Dernières erreurs
sudo journalctl -u teleinfo-listener -p err -n 50
```

### Vérifier le service
```bash
# Statut
sudo systemctl status teleinfo-listener

# Redémarrer
sudo systemctl restart teleinfo-listener
```

---

## Configuration hardware

Voir : [docs/hardware/teleinfo_branchement.md](../hardware/teleinfo_branchement.md)

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
