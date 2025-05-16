#!/bin/bash
# Configuration de l'environnement virtuel (venv) pour HouseBrain

cd /home/admin/housebrain/backend

# Vérification et création du venv
if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
    echo "Environnement virtuel créé avec succès."
else
    echo "L'environnement virtuel existe déjà."
fi

# Activation du venv
source .venv/bin/activate

# Installation de wheel pour éviter les warnings
pip install --upgrade pip
pip install wheel

# Installation des dépendances
echo "Installation des dépendances depuis requirements.txt..."
pip install -r requirements.txt

echo "L'environnement virtuel est prêt."
