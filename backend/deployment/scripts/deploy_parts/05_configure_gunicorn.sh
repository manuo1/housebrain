#!/bin/bash
# Configuration de Gunicorn dans le venv

# Activation de l'environnement virtuel
source /home/admin/housebrain/backend/.venv/bin/activate

# Vérification de l'installation de Gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn non détecté, installation en cours..."
    pip install gunicorn
    echo "Gunicorn installé avec succès."
else
    echo "Gunicorn est déjà installé."
fi

# Copie des fichiers de configuration
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
