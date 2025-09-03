#!/bin/bash
# Configuration du fichier .env
cd /home/admin/housebrain/backend
if [ ! -f ".env" ]; then
    cp .env.example .env
    NEW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_SECRET_KEY|" .env
    echo "Fichier .env créé avec une nouvelle SECRET_KEY"
fi

# Ajout de l'adresse IP dans le .env
ip=$(hostname -I | awk '{print $1}')
if ! grep -q "^LOCAL_IP=" ".env"; then
    echo -e "\n# Adresse IP locale du Raspberry Pi" >> ".env"
    echo "LOCAL_IP=$ip" >> ".env"
    echo "IP ajoutée dans .env"
else
    echo "IP déjà présente dans .env"
fi

# Ajout de l'adresse IP publique dans le .env
ip_public=$(curl -4 -s ifconfig.me)
if ! grep -q "^PUBLIC_IP=" ".env"; then
    echo -e "\n# Adresse IP publique du Raspberry Pi" >> ".env"
    echo "PUBLIC_IP=$ip_public" >> ".env"
    echo "Adresse IP publique ajoutée dans .env"
else
    echo "Adresse IP publique déjà présente dans .env"
fi