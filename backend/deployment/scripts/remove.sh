#!/bin/bash
# Script de désinstallation complète de HouseBrain sur Raspberry Pi

# Arrêter en cas d'erreur
set -e
cd ~

# Couleurs
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "${GREEN}[✔] $1${NC}"
}

print_step "Suppression complète de HouseBrain..."

# Arrêt et suppression de Nginx
print_step "Arrêt et suppression de Nginx..."
sudo systemctl stop nginx
sudo systemctl disable nginx
sudo apt remove nginx -y
sudo apt purge nginx -y
sudo apt autoremove --purge -y
sudo rm -rf /etc/nginx
sudo rm -rf /var/log/nginx
sudo rm -rf /var/www/html
sudo find / -name "*nginx*" -exec rm -rf {} \; || true

# Arrêt et suppression de Gunicorn
print_step "Arrêt et suppression de Gunicorn..."
sudo systemctl stop gunicorn
sudo systemctl disable gunicorn
sudo rm /etc/systemd/system/gunicorn.service || true
sudo systemctl daemon-reload
sudo pkill gunicorn || true
sudo rm /run/gunicorn.sock || true

# Suppression de HouseBrain
print_step "Suppression du dossier HouseBrain..."
sudo rm -rf /home/admin/housebrain

# Arrêt et suppression de Redis
print_step "Arrêt et suppression de Redis..."
sudo systemctl stop redis-server
sudo systemctl disable redis-server
sudo apt-get remove --purge -y redis-server
sudo apt-get autoremove -y
sudo apt-get autoclean -y
print_step "Suppression des fichiers de configuration et logs de Redis..."
sudo rm -rf /etc/redis/
sudo rm -rf /var/lib/redis/
sudo rm -rf /var/log/redis/
print_step "Suppression de l'utilisateur Redis..."
sudo userdel -r redis 2>/dev/null || echo "L'utilisateur 'redis' n'existe pas."
if ! command -v redis-server &> /dev/null; then
    print_step "Redis désinstallé avec succès."
else
    echo "Redis est toujours présent. Vérifiez manuellement."
fi

print_step "Suppression complète terminée."
print_step "Merci de redémarrer le Raspberry avant toute nouvelle installation."
