#!/bin/bash
# Script de mise à jour pour HouseBrain (backend + frontend)
# Récupère le dernier code depuis le repo, puis rejoue TOUS les modules de
# deploy_parts (mêmes modules idempotents que deploy.sh) : ça garantit que toute
# modif de config (systemd, nginx, certbot, permissions...) poussée sur le repo
# est bien appliquée ici, pas seulement le code Python/JS.

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

REPO_DIR="/home/admin/housebrain"

echo -e "${GREEN}[✔] Mise à jour de HouseBrain...${NC}"

cd "$REPO_DIR"

# Sécurité : ce Pi ne doit jamais avoir de modif locale (tout vient du repo distant).
# Si des modifs locales traînent, on arrête plutôt que de les écraser silencieusement.
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}[✘] Des modifications locales existent dans le repo, update annulé.${NC}"
    echo "Ce Pi ne devrait jamais avoir de modif locale (tout vient du repo distant)."
    git status --porcelain
    exit 1
fi

echo "Récupération du dernier code..."
git pull

bash "$REPO_DIR/backend/deployment/scripts/run_deploy_parts.sh"

echo -e "${GREEN}[✔] Mise à jour terminée.${NC}"
