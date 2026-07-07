##  **Voir les logs en temps réel :**
### **Nginx :**
Affiche les logs du serveur web Nginx.
```bash
sudo journalctl -u nginx -f
```
---
### **Gunicorn :**
Affiche les logs du serveur d'application Gunicorn.
```bash
sudo journalctl -u gunicorn -f
```
---
### **Teleinfo Listener :**
Affiche les logs du listener Teleinfo.
```bash
sudo journalctl -u teleinfo-listener -f
```
---
### **Bluetooth Listener :**
Affiche les logs du listener Bluetooth.
```bash
sudo journalctl -u bluetooth-listener -f
```
---
### **Redis :**
Affiche les logs du serveur Redis.
```bash
sudo journalctl -u redis-server -f
```
---
### **Scheduler (tâches périodiques) :**
Affiche les logs du Scheduler.
```bash
sudo journalctl -u housebrain-periodic -f
```
**Voir la prochaine exécution du timer** :
```bash
systemctl list-timers housebrain-periodic.timer
```
Version détaillée des logs.
```bash
sudo journalctl -u gunicorn -f -o json-pretty --no-pager
```
---
## **Persistance des logs (journald) :**
Les logs journald sont configurés en persistant (`/etc/systemd/journald.conf`, `Storage=persistent`) : ils survivent aux reboots et aux freezes, contrairement au mode par défaut (RAM uniquement).

**Espace disque utilisé par les logs** :
```bash
journalctl --disk-usage
```

**Purge** : automatique, gérée par journald (`SystemMaxUse=100M`, `SystemMaxFileSize=20M`, `MaxRetentionSec=30day`). Aucune action manuelle nécessaire.

---
## **Lire les logs après un freeze/reboot :**
**Lister tous les boots enregistrés** :
```bash
journalctl --list-boots
```

**Logs du boot précédent** (utile après un freeze) :
```bash
journalctl -b -1
```

**Logs du boot actuel uniquement** :
```bash
journalctl -b
```

---
## **Filtrer les logs :**
**Par période** :
```bash
journalctl --since "1 hour ago"
journalctl --since "2026-07-07 08:00:00" --until "2026-07-07 09:00:00"
```

**Par niveau de sévérité** (erreurs et plus grave) :
```bash
journalctl -p err
```

**Combiner service + période + niveau** :
```bash
journalctl -u housebrain-periodic.service --since "1 hour ago" -p warning
```

---
## **Métriques système (température, RAM, disque, charge, USB) :**
Loguées automatiquement à chaque exécution du Scheduler (1x/minute), via `core/services/system_metrics.py`. Visibles dans les logs du Scheduler :
```bash
sudo journalctl -u housebrain-periodic -f
```

En cas de throttling, sous-tension ou erreur USB détectée, la ligne remonte en `warning` (donc visible avec `-p warning`), sinon en `info`.

**Vérifier manuellement l'état de l'alimentation/throttling** :
```bash
vcgencmd get_throttled
vcgencmd measure_temp
```
