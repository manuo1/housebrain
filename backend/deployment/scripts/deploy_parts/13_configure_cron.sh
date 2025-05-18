#!/bin/bash
# Configuration du cron pour les tâches périodiques Django


# Création du fichier de log s'il n'existe pas
mkdir -p "/home/admin/housebrain/backend/logs/"
touch "/home/admin/housebrain/backend/logs/cron_tasks.log"

# Suppression de l'ancienne tâche (si elle existe déjà)
crontab -l | grep -v "manage.py periodic_tasks" | crontab -

# Ajout de la nouvelle tâche dans le cron
* * * * * cd /home/admin/housebrain/backend && /home/admin/housebrain/backend/.venv/bin/python manage.py periodic_tasks 2>&1 | sed "s/^/$(date +\%Y-\%m-\%d\ \%H:\%M:\%S) /" >> /home/admin/housebrain/backend/logs/cron_tasks.log
                                                                                
echo "Cron configuré pour exécuter les tâches périodiques chaque minute."
