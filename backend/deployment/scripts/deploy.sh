#!/bin/bash
# Script principal de déploiement initial pour HouseBrain
# Suppose que le repo est déjà cloné dans /home/admin/housebrain (première étape
# manuelle, ne peut pas être auto-bootstrappée par un script qui vit dans le repo
# lui-même). Exécute ensuite tous les modules de deploy_parts (idempotents).

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}[✔] Déploiement de HouseBrain...${NC}"

bash /home/admin/housebrain/backend/deployment/scripts/run_deploy_parts.sh

echo -e "${GREEN}[✔] Déploiement terminé ! Vous pouvez accéder à HouseBrain sur :${NC}"
echo -e "${GREEN}http://$(hostname -I | awk '{print $1}')/ ${NC}ou ${GREEN}http://housebrain/${NC}"
