#!/bin/bash
# Script de vérification global pour HouseBrain

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_success() {
    echo -e "${GREEN}[✔] $1${NC}"
}

function print_error() {
    echo -e "${RED}[✘] $1${NC}"
}

print_success "Vérification globale de HouseBrain..."

# 🔹 Vérification des services
SERVICES=("nginx" "gunicorn" "redis-server" "teleinfo-listener")

for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        print_success "$service est actif."
    else
        print_error "$service n'est pas actif."
    fi
done

# 🔹 Vérification de l'application Django
APP_URL="http://$(hostname -I | awk '{print $1}')/"

if curl --output /dev/null --silent --head --fail "$APP_URL"; then
    print_success "L'application HouseBrain est accessible à $APP_URL"
else
    print_error "L'application HouseBrain n'est pas accessible."
fi

# 🔹 Vérification des fichiers essentiels
FILES=(
    "/home/admin/housebrain/backend/.env"
    "/home/admin/housebrain/backend/db.sqlite3"
    "/etc/nginx/sites-available/housebrain"
    "/etc/systemd/system/gunicorn.service"
    "/etc/systemd/system/teleinfo-listener.service"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Le fichier $file est présent."
    else
        print_error "Le fichier $file est manquant."
    fi
done

# 🔹 Vérification des répertoires
DIRS=(
    "/home/admin/housebrain/backend/media"
    "/home/admin/housebrain/backend/deployment"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Le répertoire $dir est présent."
    else
        print_error "Le répertoire $dir est manquant."
    fi
done

print_success "Vérification complète terminée."
