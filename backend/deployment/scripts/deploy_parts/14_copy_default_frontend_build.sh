#!/bin/bash
# Crée une page de fallback si aucun frontend n'a encore été déployé.
# Sécurité : ne touche JAMAIS à un frontend déjà présent (plus de rm -rf inconditionnel).
# Idempotent et rejouable sans risque : devient un no-op dès que 16_deploy_frontend.sh
# a déployé un vrai build.

set -e

FRONTEND_DIR="/var/www/housebrain-frontend"

if [ -d "$FRONTEND_DIR" ] && [ -n "$(ls -A "$FRONTEND_DIR" 2>/dev/null)" ]; then
    echo "[INFO] Un frontend est déjà présent dans $FRONTEND_DIR, fallback ignoré (rien écrasé)."
    exit 0
fi

echo "[INFO] Aucun frontend déployé, création d'une page de fallback dans $FRONTEND_DIR"
sudo mkdir -p "$FRONTEND_DIR"

sudo tee "$FRONTEND_DIR/index.html" > /dev/null << EOF
<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <title>HouseBrain - Front absent</title>
  </head>
  <body>
    <h1>Le frontend n'est pas encore déployé.</h1>
  </body>
</html>
EOF

echo "[INFO] Fallback déployé."
