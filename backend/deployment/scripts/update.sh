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

# Ignore les changements de bit exécutable (chmod +x appliqué par run_deploy_parts.sh
# à chaque exécution) : les scripts sont commités depuis Windows sans ce bit, donc
# Git le voit sinon comme une modif locale alors que le contenu n'a pas changé.
git config core.fileMode false

# Sécurité : ce Pi ne doit jamais avoir de modif locale (tout vient du repo distant).
# Si des modifs locales traînent, on arrête plutôt que de les écraser silencieusement.
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}[✘] Des modifications locales existent dans le repo, update annulé.${NC}"
    echo "Ce Pi ne devrait jamais avoir de modif locale (tout vient du repo distant)."
    git status --porcelain
    exit 1
fi

# Backup de la base avant toute migration éventuelle (écrase la précédente sauvegarde,
# pas d'historique conservé - juste un filet de sécurité pour le dernier update en date).
echo "Sauvegarde de db.sqlite3 avant mise à jour..."
cp "$REPO_DIR/backend/db.sqlite3" "$REPO_DIR/backend/db.sqlite3.pre-update-bak"

echo "Récupération du dernier code..."
git pull

bash "$REPO_DIR/backend/deployment/scripts/run_deploy_parts.sh"

echo -e "${GREEN}[✔] Mise à jour terminée.${NC}"
