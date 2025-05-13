#!/bin/bash
# Script de déploiement pour HouseBrain sur Raspberry Pi

# Arrêter en cas d'erreur
set -e

echo "Déploiement de HouseBrain..."

# Mise à jour système
echo "Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

# Installation des dépendances
echo "Installation des dépendances..."
sudo apt install -y python3-pip python3-venv nginx

# Configuration Nginx
echo "Configuration de Nginx..."
sudo cp /home/admin/housebrain/backend/deployment/nginx/housebrain.conf /etc/nginx/sites-available/housebrain
sudo ln -sf /etc/nginx/sites-available/housebrain /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Configuration Gunicorn
echo "Configuration de Gunicorn..."
sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload

# Configuration de l'environnement Django
echo "Configuration de Django..."
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
    echo "Fichier .env créé avec une nouvelle SECRET_KEY"
fi

# Migrations et collecte des fichiers statiques
python manage.py migrate
python manage.py collectstatic --no-input

# Permissions
sudo chown -R admin:www-data /home/admin/housebrain
chmod 664 /home/admin/housebrain/backend/db.sqlite3
chmod 775 /home/admin/housebrain/backend
sudo chmod 775 /home/admin/housebrain/backend/media

# Démarrer et activer Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn

echo "Déploiement terminé ! Accédez à http://housebrain.local/"