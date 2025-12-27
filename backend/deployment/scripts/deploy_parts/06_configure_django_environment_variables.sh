#!/bin/bash
# Configuration du fichier .env

cd /home/admin/housebrain/backend

# Création du .env depuis .env.example si absent
if [ ! -f ".env" ]; then
    cp .env.example .env
    NEW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_SECRET_KEY|" .env
    echo "Fichier .env créé avec une nouvelle SECRET_KEY"
fi

# Ajout/mise à jour de l'adresse IP locale
ip=$(hostname -I | awk '{print $1}')
if grep -q "^LOCAL_IP=" ".env"; then
    sed -i "s|^LOCAL_IP=.*|LOCAL_IP=$ip|" .env
    echo "IP locale mise à jour dans .env: $ip"
else
    echo -e "\n# Adresse IP locale du Raspberry Pi" >> ".env"
    echo "LOCAL_IP=$ip" >> ".env"
    echo "IP locale ajoutée dans .env: $ip"
fi

# Ajout/mise à jour de l'adresse IP publique
ip_public=$(curl -4 -s ifconfig.me)
if grep -q "^PUBLIC_IP=" ".env"; then
    sed -i "s|^PUBLIC_IP=.*|PUBLIC_IP=$ip_public|" .env
    echo "IP publique mise à jour dans .env: $ip_public"
else
    echo -e "\n# Adresse IP publique du Raspberry Pi" >> ".env"
    echo "PUBLIC_IP=$ip_public" >> ".env"
    echo "Adresse IP publique ajoutée dans .env: $ip_public"
fi

# Rappel pour la configuration DOMAINS (si HTTPS)
if ! grep -q "^DOMAINS=" ".env" || grep -q "^DOMAINS=ma-super-app.fr" ".env"; then
    echo ""
    echo "⚠️  IMPORTANT: Si vous utilisez HTTPS, modifiez la variable DOMAINS dans .env"
    echo "   Exemple: DOMAINS=housebrain.emmanuel-oudot.fr"
    echo "   Cette valeur doit correspondre à votre configuration Nginx."
fi

echo "Configuration .env terminée."
