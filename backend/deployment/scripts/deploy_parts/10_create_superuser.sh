#!/bin/bash
# Création du superutilisateur Django

echo "Création du superutilisateur Django..."

cd /home/admin/housebrain/backend

# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer la commande pour créer le superuser
echo "Veuillez entrer les informations pour le superutilisateur :"
python manage.py createsuperuser

# Désactiver l'environnement virtuel
deactivate

echo "Superutilisateur Django créé avec succès."
