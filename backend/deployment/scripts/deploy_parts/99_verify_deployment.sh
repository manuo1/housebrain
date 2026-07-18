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
# Utilise le bon en-tête Host pour que nginx route vers le bon vhost : depuis que
# Certbot gère --redirect, un Host qui ne correspond pas au domaine configuré
# tombe sur un 404 (comportement voulu de Certbot, pas un souci applicatif).
# Retry avec un court délai : juste après un (re)démarrage de gunicorn/nginx,
# le premier appel peut échouer le temps que le service soit pleinement prêt.
cd /home/admin/housebrain/backend
source .env 2>/dev/null || true

if [ -n "$DOMAINS" ] && [ "$DOMAINS" != "ma-super-app.fr,www.ma-super-app.fr" ]; then
    CHECK_HOST=$(echo "$DOMAINS" | cut -d',' -f1)
else
    CHECK_HOST=$(hostname -I | awk '{print $1}')
fi

APP_URL="http://127.0.0.1/backend/admin/"
APP_OK=0

for attempt in 1 2 3 4 5; do
    if curl --output /dev/null --silent --head --fail -H "Host: $CHECK_HOST" "$APP_URL"; then
        APP_OK=1
        break
    fi
    sleep 2
done

if [ "$APP_OK" = "1" ]; then
    print_success "L'application HouseBrain est accessible (Host: $CHECK_HOST)"
else
    print_error "L'application HouseBrain n'est pas accessible (Host: $CHECK_HOST, après 5 tentatives)."
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
