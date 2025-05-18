#!/bin/bash
# Script de mise à jour pour HouseBrain

# Arrêter en cas d'erreur
set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "${GREEN}[✔] $1${NC}"
}

function print_error() {
    echo -e "${RED}[✘] $1${NC}"
}

print_step "Mise à jour de HouseBrain..."

# 🔹 Gestion du cron
print_step "Suppression du cron..."

# Supprimer de la tâche cron
if crontab -l | grep -q "manage.py periodic_tasks"; then
    crontab -l | grep -v "manage.py periodic_tasks" | crontab -
    print_step "Ancienne tâche cron supprimée."
else
    print_step "Aucune tâche cron existante trouvée."
fi


# 🔹 Arrêt des services
print_step "Arrêt des services..."
sudo systemctl stop nginx
sudo systemctl stop gunicorn
sudo systemctl stop teleinfo-listener.service
sudo systemctl stop bluetooth-listener.service

# 🔹 Mise à jour du dépôt
print_step "Mise à jour du code source depuis Git..."
cd /home/admin/housebrain
git fetch --all
git reset --hard origin/main
git pull origin main

# 🔹 Mise à jour de l'environnement virtuel
print_step "Activation de l'environnement virtuel..."
cd backend
source .venv/bin/activate

print_step "Mise à jour des dépendances..."
pip install -r requirements.txt

# 🔹 Migrations Django et collectstatic
print_step "Application des migrations..."
python manage.py migrate

print_step "Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

# 🔹 Redémarrage des services
print_step "Redémarrage des services..."
sudo systemctl start nginx
sudo systemctl start gunicorn
sudo systemctl start teleinfo-listener.service
sudo systemctl start bluetooth-listener.service

# 🔹 Vérification des statuts
print_step "Vérification des statuts des services..."
sudo systemctl status nginx --no-pager
sudo systemctl status gunicorn --no-pager
sudo systemctl status teleinfo-listener.service --no-pager
sudo systemctl status bluetooth-listener.service --no-pager

# Recréer la tâche cron
CRON_CMD="* * * * * cd /home/admin/housebrain/backend && /home/admin/housebrain/backend/.venv/bin/python manage.py periodic_tasks 2>&1 | sed \"s/^/$(date +\%Y-\%m-\%d\ \%H:\%M:\%S) /\" >> /home/admin/housebrain/backend/logs/cron_tasks.log"
(crontab -l; echo "$CRON_CMD") | crontab -

print_step "Tâche cron configurée."

print_step "Mise à jour de HouseBrain terminée avec succès !"
