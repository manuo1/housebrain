# Scheduler

Orchestrateur de tâches périodiques pour HouseBrain.

---

## Vue d'ensemble

Le scheduler exécute automatiquement des tâches de maintenance et de synchronisation à intervalles réguliers via un service systemd dédié.

---

## Architecture

### Service systemd dédié
Le scheduler fonctionne via un service systemd dédié (`housebrain-periodic`) déclenché par un timer à intervalles réguliers.

**Composants :**
- `housebrain-periodic.timer` : Timer systemd qui déclenche l'exécution
- `housebrain-periodic.service` : Service systemd qui exécute la commande Django
- `periodic_tasks.py` : Commande Django qui orchestre les tâches

---

## Configuration

### Timer systemd

**Fréquence :** Toutes les 1 minute

```ini
[Timer]
OnCalendar=*:0/1
Persistent=true
AccuracySec=1s
```

### Localisation
```
backend/scheduler/management/commands/periodic_tasks.py
```

---

## Fonctionnement

### Exécution des tâches
Les tâches sont exécutées séquentiellement dans l'ordre défini, sans isolation entre elles : il n'y a volontairement aucun `try/except` autour de chaque étape. Si une tâche lève une exception, l'exécution s'arrête immédiatement et les tâches suivantes ne sont **pas** exécutées ce cycle-là (le cycle suivant, une minute plus tard, repart normalement).

Ce choix est assumé : une tâche qui plante silencieusement sur un état incohérent est considérée plus dangereuse qu'un cycle sauté. Cela signifie aussi qu'un échec dans une tâche (ex : synchronisation matérielle des radiateurs) empêche les tâches suivantes de s'exécuter ce cycle-là (ex : `log_system_metrics`), même si elles n'ont aucun rapport entre elles.

Les détails des tâches orchestrées sont documentés dans leur section respective.

---

## Logs

### Consulter les exécutions
```bash
# Logs temps-réel
sudo journalctl -u housebrain-periodic -f

# Dernières exécutions
sudo journalctl -u housebrain-periodic -n 50 --no-pager
```

### Vérifier le timer
```bash
# Statut du timer
sudo systemctl status housebrain-periodic.timer

# Prochaine exécution
systemctl list-timers housebrain-periodic.timer
```

---

## Gestion du service

### Contrôle
```bash
# Démarrer
sudo systemctl start housebrain-periodic.timer

# Arrêter
sudo systemctl stop housebrain-periodic.timer

# Redémarrer
sudo systemctl restart housebrain-periodic.timer

# Désactiver
sudo systemctl disable housebrain-periodic.timer
```

### Exécution manuelle
```bash
cd /home/admin/housebrain/backend
source .venv/bin/activate
python manage.py periodic_tasks
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
