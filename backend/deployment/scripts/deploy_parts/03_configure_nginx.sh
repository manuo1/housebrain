#!/bin/bash
# Configuration complète de Nginx

# Vérification si Nginx est déjà installé
if ! nginx -v &> /dev/null; then
    echo "Nginx non détecté, installation en cours..."
    sudo apt update
    sudo apt install -y nginx
    echo "Nginx installé avec succès."
else
    echo "Nginx est déjà installé."
fi

# Supprimer le site par défaut de Nginx s'il existe
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    echo "Suppression du site par défaut de Nginx..."
    sudo rm /etc/nginx/sites-enabled/default
fi

# Copier la configuration de HouseBrain
if [ -f "/home/admin/housebrain/backend/deployment/nginx/housebrain" ]; then
    sudo cp /home/admin/housebrain/backend/deployment/nginx/housebrain /etc/nginx/sites-available/housebrain
    sudo ln -sf /etc/nginx/sites-available/housebrain /etc/nginx/sites-enabled/
    echo "Configuration de Nginx appliquée."
else
    echo "Erreur : le fichier de configuration nginx 'housebrain' est introuvable."
    exit 1
fi

# Vérification de la configuration et redémarrage de Nginx
sudo nginx -t && sudo systemctl restart nginx

# Vérification du service
if systemctl is-active --quiet nginx; then
    echo "Nginx est actif."
else
    echo "Nginx n'a pas démarré correctement."
fi
