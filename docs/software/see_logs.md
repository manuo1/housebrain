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
Les logs journald sont configurés en persistant : ils survivent aux reboots et aux freezes, contrairement au mode par défaut (RAM uniquement, perdus à chaque redémarrage).

**Piège Raspberry Pi OS** : le système fournit `/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` (`Storage=volatile`). Les drop-ins `.conf.d/` s'appliquent APRÈS `/etc/systemd/journald.conf` et l'écrasent : modifier `journald.conf` seul n'a aucun effet.

**Config en place** : drop-in `/etc/systemd/journald.conf.d/99-housebrain.conf` (les drop-ins sont triés par nom : le préfixe `99` le fait passer après celui de Pi OS (`40-…`), mais `syslog.conf` (dans `/usr/lib`) passe encore après, sans toucher à `Storage` ; `apt` ne modifie pas un fichier de `/etc` qu'aucun paquet ne fournit). Il est écrit et vérifié par `deploy_parts/01b_configure_journald.sh`, rejoué à chaque update. Contenu : `Storage=persistent`, `SystemMaxUse=100M`, `SystemMaxFileSize=20M`, `MaxRetentionSec=30day`, `Compress=yes`.

**Vérifier la config EFFECTIVE** (tous fichiers fusionnés, la dernière valeur de `Storage=` gagne) :
```bash
systemd-analyze cat-config systemd/journald.conf | grep -E '^(Storage|SystemMax|MaxRetention|Compress)'
```

**Vérifier que le journal est bien sur disque** (doit lister un `system.journal`, pas `/run/log/journal`) :
```bash
ls /var/log/journal/*/
```

Si `01b` sort en erreur (`Storage effectif ≠ persistent`), un autre fichier de conf passe après le drop-in : `systemd-analyze cat-config systemd/journald.conf | grep -nE '^(#|Storage=)'` montre lequel. `99_verify_deployment.sh` contrôle aussi ces deux points.

**Espace disque utilisé par les logs** :
```bash
journalctl --no-pager --disk-usage
```

**Purge** : automatique, gérée par journald (`SystemMaxUse=100M`, `SystemMaxFileSize=20M`, `MaxRetentionSec=30day`). Aucune action manuelle nécessaire.

---
## **Lire les logs après un freeze/reboot :**
**Lister tous les boots enregistrés** :
```bash
journalctl --no-pager --list-boots
```

**Dernières lignes du boot précédent** (juste avant la coupure) :
```bash
journalctl --no-pager -b -1 -n 100
```

**Messages kernel du boot précédent** (erreurs disque, USB, sous-tension) :
```bash
journalctl --no-pager -k -b -1 -n 100
```

**État d'alimentation et USB juste avant la coupure** (dernières lignes `[Monitoring]` du boot précédent) :
```bash
journalctl --no-pager -b -1 -u housebrain-periodic | grep "\[Monitoring\]" | tail -5
```

**Logs du boot actuel uniquement** :
```bash
journalctl --no-pager -b
```

**Piège de l'horloge** : le Pi n'a pas d'horloge matérielle (RTC). Au boot, l'heure est celle sauvegardée par `fake-hwclock` jusqu'à la synchro NTP : le premier timestamp d'un boot peut être faux (un boot du matin peut s'afficher la veille au soir). Pour retrouver un incident, utiliser `--list-boots` et `-b -1` plutôt que des `--since`.

**Disque qui décroche** (SSD USB) : symptômes = page 500 nginx (nginx ne relit plus ses fichiers), SSH fermé avant la bannière, `cat` en `Input/output error`, et sur la console HDMI (`tty1`) `EXT4-fs (sda2): shut down requested`. Le système de fichiers racine est alors inutilisable : les dernières lignes avant la coupure peuvent ne pas avoir été écrites, et la console HDMI est la seule trace de l'erreur (la photographier avant de couper l'alim). Après redémarrage, lire les messages kernel du boot précédent (commande ci-dessus), puis `lsusb` (adaptateur USB) et `vcgencmd get_throttled` (alimentation, compteur remis à zéro à chaque boot).

---
## **Filtrer les logs :**
**Par période** :
```bash
journalctl --no-pager --since "1 hour ago"
journalctl --no-pager --since "2026-07-07 08:00:00" --until "2026-07-07 09:00:00"
```

**Par niveau de sévérité** (erreurs et plus grave) :
```bash
journalctl --no-pager -p err
```

**Combiner service + période + niveau** :
```bash
journalctl --no-pager -u housebrain-periodic.service --since "1 hour ago" -p warning
```

**Par label applicatif** (les labels sont dans `core/constants.py`, `LoggerLabel`) : `[Shelly Driver]` apparaît dans l'unité `gunicorn` (appels de l'API) et dans `housebrain-periodic` (pilotage du chauffe-eau) ; `[Monitoring]` et `[Periodic Tasks]` dans `housebrain-periodic`.
```bash
journalctl --no-pager -u gunicorn --since "1 hour ago" | grep "Shelly Driver" | tail -15
journalctl --no-pager -u housebrain-periodic --since "1 hour ago" | grep "\[Monitoring\]" | tail -5
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
