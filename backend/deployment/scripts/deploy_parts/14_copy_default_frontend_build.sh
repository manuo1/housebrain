#!/bin/bash
# Copy fallback index.html with cleanup

set -e

sudo rm -rf /var/www/housebrain-frontend
sudo mkdir -p /var/www/housebrain-frontend

echo "[INFO] Creating fallback index.html in /var/www/housebrain-frontend"

sudo tee /var/www/housebrain-frontend/index.html > /dev/null << EOF
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

echo "[INFO] Fallback deployed."
