#!/bin/bash
# Installation et configuration de Gunicorn

# Vérification si Gunicorn est déjà installé
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn non détecté, installation en cours..."
    pip install gunicorn
    echo "Gunicorn installé avec succès."
else
    echo "Gunicorn est déjà installé."
fi

# Copier les fichiers de service
sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.socket /etc/systemd/system/
sudo cp /home/admin/housebrain/backend/deployment/gunicorn/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Vérification du service
if systemctl is-active --quiet gunicorn; then
    echo "Gunicorn est actif."
else
    echo "Gunicorn n'a pas démarré correctement."
fi
