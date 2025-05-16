#!/bin/bash
# Configuration de l'environnement Django

cd /home/admin/housebrain/backend

# Création de l'environnement virtuel si nécessaire
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activation de l'environnement virtuel
source .venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Fichier .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    NEW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_SECRET_KEY|" .env
    echo "Fichier .env créé avec une nouvelle SECRET_KEY"
fi

# Ajout de l'IP locale dans .env
ip=$(hostname -I | awk '{print $1}')
if ! grep -q "^RASPBERRYPI_LOCAL_IP=" ".env"; then
    echo -e "\n# Adresse IP locale du Raspberry Pi" >> ".env"
    echo "RASPBERRYPI_LOCAL_IP=$ip" >> ".env"
    echo "IP ajoutée dans .env"
else
    echo "IP déjà présente dans .env"
fi

# Migrations et collecte des statiques
python manage.py migrate
python manage.py collectstatic --no-input

echo "Django configuré avec succès."
