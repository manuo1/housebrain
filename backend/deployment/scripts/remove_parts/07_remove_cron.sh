#!/bin/bash
# Suppression du cron pour les tâches périodiques Django

# Vérification de l'existence du cron
if crontab -l | grep -q "manage.py periodic_tasks"; then
    # Suppression de la tâche spécifique
    crontab -l | grep -v "manage.py periodic_tasks" | crontab -
    echo "Le cron manage.py periodic_tasks a été supprimé."
else
    echo "Aucune tâche cron manage.py periodic_tasks trouvée."
fi
