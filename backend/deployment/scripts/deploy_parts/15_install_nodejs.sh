#!/bin/bash
# Installation de Node.js pour le frontend React

set -e

NODE_VERSION="20.x"

echo "Vérification de Node.js..."

# Vérifier si Node.js est déjà installé
if command -v node &> /dev/null; then
    CURRENT_VERSION=$(node --version)
    echo "Node.js est déjà installé : $CURRENT_VERSION"

    # Vérifier npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo "npm est installé : $NPM_VERSION"
        echo "Installation de Node.js ignorée."
        exit 0
    fi
fi

echo "Installation de Node.js $NODE_VERSION..."

# Télécharger et exécuter le script d'installation NodeSource
curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION} | sudo -E bash -

# Installer Node.js
sudo apt-get install -y nodejs

# Vérification de l'installation
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    echo "Node.js installé avec succès : $(node --version)"
    echo "npm installé avec succès : $(npm --version)"
else
    echo "Erreur lors de l'installation de Node.js"
    exit 1
fi
