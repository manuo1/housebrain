#!/bin/bash
# Déploiement du frontend React

set -e

FRONTEND_DIR="/home/admin/housebrain/frontend"
DEPLOY_DIR="/var/www/housebrain-frontend"

echo "Déploiement du frontend React..."

# Vérifier que Node.js est installé
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "Erreur : Node.js ou npm n'est pas installé."
    echo "Le fallback HTML restera en place."
    exit 1
fi

# Vérifier que le dossier frontend existe
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Erreur : Le dossier frontend n'existe pas : $FRONTEND_DIR"
    echo "Le fallback HTML restera en place."
    exit 1
fi

# Se placer dans le dossier frontend
cd "$FRONTEND_DIR"

# Installer les dépendances npm
echo "Installation des dépendances npm..."
npm install

# Build du frontend
echo "Build du frontend React..."
npm run build

# Vérifier que le build a créé le dossier dist
if [ ! -d "$FRONTEND_DIR/dist" ]; then
    echo "Erreur : Le build n'a pas créé le dossier dist."
    echo "Le fallback HTML restera en place."
    exit 1
fi

# Déployer le build
echo "Déploiement du build dans $DEPLOY_DIR..."
sudo rm -rf "$DEPLOY_DIR"/*
sudo cp -r "$FRONTEND_DIR/dist"/* "$DEPLOY_DIR/"

# Vérifier que le déploiement a réussi
if [ -f "$DEPLOY_DIR/index.html" ]; then
    echo "Frontend React déployé avec succès."
else
    echo "Erreur : Le déploiement du frontend a échoué."
    exit 1
fi
