#!/bin/bash
# Configuration de Django pour HouseBrain

# Activation de l'environnement virtuel
source /home/admin/housebrain/backend/.venv/bin/activate

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
if ! grep -q "^RASPBERRYPI_LOCAL_IP=" ".env"; then
    echo -e "\n# Adresse IP locale du Raspberry Pi" >> ".env"
    echo "RASPBERRYPI_LOCAL_IP=$ip" >> ".env"
    echo "IP ajoutée dans .env"
else
    echo "IP déjà présente dans .env"
fi

# Migrations et collecte des fichiers statiques
echo "Application des migrations Django..."
python manage.py migrate
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "Django configuré avec succès."
