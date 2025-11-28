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

# Gestion du systemd timer
print_step "Arrêt du systemd timer..."
if systemctl is-active --quiet housebrain-periodic.timer; then
    sudo systemctl stop housebrain-periodic.timer
    print_step "Timer arrêté."
else
    print_step "Timer déjà arrêté ou non configuré."
fi

# Arrêt des services
print_step "Arrêt des services..."
sudo systemctl stop nginx
sudo systemctl stop gunicorn
sudo systemctl stop teleinfo-listener.service
sudo systemctl stop bluetooth-listener.service
sudo systemctl stop housebrain-periodic.timer

# Mise à jour du dépôt
print_step "Mise à jour du code source depuis Git..."
cd /home/admin/housebrain
git fetch --all
git reset --hard origin/main
git pull origin main

# Mise à jour de l'environnement virtuel
print_step "Activation de l'environnement virtuel..."
cd backend
source .venv/bin/activate

print_step "Mise à jour des dépendances..."
pip install -r requirements.txt

# Migrations Django et collectstatic
print_step "Application des migrations..."
python manage.py migrate

print_step "Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

# Redémarrage des services
print_step "Redémarrage des services..."
sudo systemctl start nginx
sudo systemctl start gunicorn
sudo systemctl start teleinfo-listener.service
sudo systemctl start bluetooth-listener.service
sudo systemctl start housebrain-periodic.timer

# Vérification des statuts
print_step "Vérification des statuts des services..."
sudo systemctl status nginx --no-pager
sudo systemctl status gunicorn --no-pager
sudo systemctl status teleinfo-listener.service --no-pager
sudo systemctl status bluetooth-listener.service --no-pager
sudo systemctl status housebrain-periodic.timer --no-pager

print_step "Mise à jour de HouseBrain terminée avec succès !"
