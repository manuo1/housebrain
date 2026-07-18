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

# Vérification des services
SERVICES=("nginx" "gunicorn" "redis-server" "teleinfo-listener" "bluetooth-listener")

for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        print_success "$service est actif."
    else
        print_error "$service n'est pas actif."
    fi
done

# Vérification de l'application Django
# Retry avec un court délai : juste après un (re)démarrage de gunicorn/nginx,
# le premier appel peut échouer le temps que le service soit pleinement prêt.
APP_URL="http://$(hostname -I | awk '{print $1}')/backend/admin/"
APP_OK=0

for attempt in 1 2 3 4 5; do
    if curl --output /dev/null --silent --head --fail "$APP_URL"; then
        APP_OK=1
        break
    fi
    sleep 2
done

if [ "$APP_OK" = "1" ]; then
    print_success "L'application HouseBrain est accessible à $APP_URL"
else
    print_error "L'application HouseBrain n'est pas accessible (après 5 tentatives)."
fi

# Vérification des fichiers essentiels
FILES=(
    "/home/admin/housebrain/backend/.env"
    "/home/admin/housebrain/backend/db.sqlite3"
    "/etc/nginx/sites-available/housebrain"
    "/etc/systemd/system/gunicorn.service"
    "/etc/systemd/system/teleinfo-listener.service"
    "/etc/systemd/system/bluetooth-listener.service"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Le fichier $file est présent."
    else
        print_error "Le fichier $file est manquant."
    fi
done

# Vérification des répertoires
DIRS=(
    "/home/admin/housebrain/backend/media"
    "/home/admin/housebrain/backend/static"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Le répertoire $dir est présent."
    else
        print_error "Le répertoire $dir est manquant."
    fi
done

print_success "Vérification complète terminée."
