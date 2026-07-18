#!/bin/bash
# Boucle d'exécution des modules de déploiement (deploy_parts).
# Utilisée à la fois par deploy.sh (installation initiale) et update.sh (mise à jour) :
# chaque module est idempotent, rejouable à tout moment sans effet de bord si déjà
# appliqué. C'est cette mise en commun qui garantit qu'une update applique bien
# TOUTE la config (systemd, nginx, certbot, permissions...), pas seulement le code.

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

function print_step()  { echo -e "${GREEN}[✔] $1${NC}"; }
function print_error() { echo -e "${RED}[✘] $1${NC}"; }
function print_warn()  { echo -e "${YELLOW}[!] $1${NC}"; }

DEPLOY_PARTS_DIR="/home/admin/housebrain/backend/deployment/scripts/deploy_parts"

chmod +x "$DEPLOY_PARTS_DIR"/*.sh

for script in "$DEPLOY_PARTS_DIR"/*.sh; do
    print_step "Exécution de $(basename "$script")"
    if bash "$script"; then
        print_step "$(basename "$script") exécuté avec succès."
    else
        exit_code=$?
        if [ "$exit_code" -eq 42 ]; then
            print_warn "$(basename "$script") demande un redémarrage avant de continuer."
            print_warn "Redémarre le Pi puis relance ce script : il est idempotent, rien ne sera refait inutilement."
            exit 42
        fi
        print_error "Échec lors de l'exécution de $(basename "$script"). Arrêt."
        exit 1
    fi
done
