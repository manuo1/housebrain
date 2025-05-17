#!/bin/bash
# Installation de Bleak dans le venv avec version spécifique

# Activation de l'environnement virtuel
source /home/admin/housebrain/backend/.venv/bin/activate

BLEAK_VERSION="0.22.3"

# Vérification de l'installation de Bleak avec la bonne version
if ! python -c "import bleak; assert bleak.__version__ == '$BLEAK_VERSION'" &> /dev/null; then
    echo "Bleak version $BLEAK_VERSION non détectée, installation en cours..."
    pip install bleak=="$BLEAK_VERSION"
    echo "Bleak version $BLEAK_VERSION installée avec succès."
else
    echo "Bleak version $BLEAK_VERSION est déjà installée."
fi
