#!/bin/bash
# Script de mise à jour pour HouseBrain sur Raspberry Pi

# Arrêter en cas d'erreur
set -e

# Couleurs
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "${GREEN}[✔] $1${NC}"
}

print_step "Arrêt de Gunicorn..."
sudo systemctl stop gunicorn

print_step "Arrêt de Teleinfo Listener..."
sudo systemctl stop teleinfo-listener

print_step "Mise à jour du code source..."
cd /home/admin/housebrain
git fetch 
git reset --hard origin/main

# Activation de l'environnement virtuel
source backend/.venv/bin/activate

print_step "Mise à jour des dépendances Python (si nécessaire)..."
pip install -r backend/requirements.txt

print_step "Application des migrations (si nécessaire)..."
cd backend
python manage.py migrate

print_step "Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

# Désactivation de l'environnement virtuel
deactivate

print_step "Redémarrage de Redis..."
sudo systemctl restart redis-server
sudo systemctl is-active --quiet redis-server && echo "Redis is running" || echo "Redis is not running"

print_step "Redémarrage de Gunicorn..."
sudo systemctl start gunicorn

print_step "Redémarrage de Nginx..."
sudo systemctl restart nginx

print_step "Redémarrage de Teleinfo Listener..."
sudo systemctl start teleinfo-listener
sudo systemctl is-active --quiet teleinfo-listener && echo "Teleinfo Listener is running" || echo "Teleinfo Listener is not running"

print_step "Mise à jour terminée avec succès !"
