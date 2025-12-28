# Monitoring système

Collecte et centralisation des logs systemd des services HouseBrain.

---

## Vue d'ensemble

Le module monitoring collecte automatiquement les logs journalctl des services systemd et les stocke en base de données pour consultation centralisée via l'admin Django.

---

## Collecte automatique

### Fréquence
La collecte est déclenchée par le scheduler toutes les 1 minute.

### Fenêtre de collecte
Logs des 2 dernières minutes pour chaque service.

L'overlap (collecte 1 min, fenêtre 2 min) garantit qu'aucun log n'est raté entre deux cycles.

---

## Services surveillés

- `bluetooth-listener.service`
- `gunicorn.service`
- `nginx.service`
- `redis-server.service`
- `teleinfo-listener.service`
- `housebrain-periodic.service`

---

## Filtrage intelligent

### Keywords importants

Seuls les logs contenant au moins un de ces mots-clés sont conservés :

**Erreurs techniques :**
- error, fail, failed, exception, traceback
- timeout, critical, crash, panic
- disconnect, killed, unreachable

**Problèmes de service :**
- restart, restarting, stopped, unhealthy
- worker, booting

**Codes HTTP :**
- 400, 401, 403, 404, 408, 409
- 500, 502, 503, 504

**Labels métier :**
- Labels définis dans l'application (LoggerLabel)

### Keywords exclus

Messages normaux filtrés :
- `.service: consumed` (consommation CPU normale)
- `available power is too low` (délestage attendu)

---

## Stockage

### Modèle SystemLog

```python
service      # Nom du service systemd
level        # Niveau (EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG)
message      # Contenu du log
logged_at    # Timestamp du log
created_at   # Timestamp d'insertion en base
```

### Contrainte unique

Les logs identiques (même service, timestamp, level, message) ne sont pas dupliqués.

---

## Consultation

### Interface admin

```
/backend/admin/monitoring/systemlog/
```

**Fonctionnalités :**
- Filtrage par service, level, date
- Recherche dans les messages
- Tri par date décroissante
- Hiérarchie par date

**Champs en lecture seule :** Tous (les logs ne sont pas modifiables).

---
