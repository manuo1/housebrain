#!/bin/bash
# Script de déploiement pour HouseBrain sur Raspberry Pi

# Arrêter en cas d'erreur
set -e

# Couleurs
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "${GREEN}[✔] $1${NC}"
}

print_step "Déploiement de HouseBrain..."

# Mise à jour système
print_step "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
print_step "Installation des dépendances..."
sudo apt install -y python3-pip python3-venv nginx

# Configuration Nginx
print_step "Configuration de Nginx..."

# Supprimer le site par défaut de Nginx s'il existe
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    print_step "Suppression du site par défaut de Nginx..."
    sudo rm /etc/nginx/sites-enabled/default
fi

sudo cp /home/admin/housebrain/backend/deployment/nginx/housebrain /etc/nginx/sites-available/housebrain
sudo ln -sf /etc/nginx/sites-available/housebrain /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Configuration Gunicorn
print_step "Configuration de Gunicorn..."
sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.socket /etc/systemd/system/
sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload

# Configuration de l'environnement Django
print_step "Configuration de Django..."
cd /home/admin/housebrain/backend

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Générer une nouvelle clé secrète
    NEW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_SECRET_KEY|" .env
    print_step "Fichier .env créé avec une nouvelle SECRET_KEY"
fi

# Ajout de l'IP locale du Raspberry dans le fichier .env
print_step "Ajout de l'adresse IP locale dans le fichier .env..."
ip=$(hostname -I | awk '{print $1}')
ENV_FILE="/home/admin/housebrain/backend/.env"

if ! grep -q "^RASPBERRYPI_LOCAL_IP=" "$ENV_FILE"; then
    echo -e "\n# Adresse IP locale du Raspberry Pi" >> "$ENV_FILE"
    echo "RASPBERRYPI_LOCAL_IP=$ip" >> "$ENV_FILE"
    print_step "IP ajoutée dans $ENV_FILE"
else
    print_step "IP déjà présente dans $ENV_FILE"
fi

# Migrations et collecte des fichiers statiques
print_step "Migrations et collecte des fichiers statiques..."
python manage.py migrate
python manage.py collectstatic --no-input

# Permissions
print_step "Configuration des permissions..."
sudo usermod -aG admin www-data
sudo chmod 750 /home/admin
sudo chown -R admin:www-data /home/admin/housebrain
chmod 664 /home/admin/housebrain/backend/db.sqlite3
chmod 775 /home/admin/housebrain/backend
mkdir -p /home/admin/housebrain/backend/media
sudo chmod 775 /home/admin/housebrain/backend/media

print_step "Rendre les scripts de désinstallions et mise à jour exécutables"
chmod +x /home/admin/housebrain/backend/deployment/scripts/remove.sh
chmod +x /home/admin/housebrain/backend/deployment/scripts/update.sh

# Démarrer et activer Gunicorn
print_step "Démarrage de Gunicorn..."
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
# Création du Super Utilisateur
print_step "Création du Super Utilisateur :"
python manage.py createsuperuser
# Terminé
print_step "Déploiement terminé ! Vous pouvez accédez à HouseBrain aux adresses http://$ip/ ou http//:housebrain/"
sudo systemctl status gunicorn

