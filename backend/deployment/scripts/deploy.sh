#!/bin/bash
# Script principal de déploiement pour HouseBrain

# Arrêter en cas d'erreur
set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_step() {
    echo -e "${GREEN}[✔] $1${NC}"
}

function print_error() {
    echo -e "${RED}[✘] $1${NC}"
}

print_step "Déploiement de HouseBrain..."

# Rendre tous les scripts exécutables (sécurisation)
chmod +x /home/admin/housebrain/backend/deployment/scripts/deploy_parts/*.sh

# Exécution des scripts de déploiement par ordre numérique
for script in /home/admin/housebrain/backend/deployment/scripts/deploy_parts/*.sh; do
    print_step "Exécution de $(basename "$script")"
    if bash "$script"; then
        print_step "$(basename "$script") exécuté avec succès."
    else
        print_error "Échec lors de l'exécution de $(basename "$script"). Arrêt du déploiement."
        exit 1
    fi
done

print_step "Déploiement terminé ! Vous pouvez accéder à HouseBrain sur :"
echo -e "${GREEN}http://$(hostname -I | awk '{print $1}')/ ${NC}ou ${GREEN}http://housebrain/${NC}"
