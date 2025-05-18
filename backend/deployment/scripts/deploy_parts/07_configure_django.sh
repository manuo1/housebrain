#!/bin/bash
# Configuration de Django pour HouseBrain

# Activation de l'environnement virtuel
source /home/admin/housebrain/backend/.venv/bin/activate

# Migrations et collecte des fichiers statiques
echo "Application des migrations Django..."
python manage.py migrate
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "Django configuré avec succès."
