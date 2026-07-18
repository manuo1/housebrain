#!/bin/bash
# Configuration de Gunicorn (service systemd)
# La version de gunicorn est gérée uniquement via requirements.txt (installé par 04_configure_venv.sh) —
# pas de check de version en dur ici, pour éviter toute divergence avec la source de vérité.

sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.socket /etc/systemd/system/
sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Vérification de l'état du service
if systemctl is-active --quiet gunicorn; then
    echo "Gunicorn démarré avec succès."
else
    echo "Gunicorn n'a pas démarré correctement."
fi
