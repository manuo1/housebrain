#!/bin/bash
# Configuration de Gunicorn dans le venv

# Activation de l'environnement virtuel
source /home/admin/housebrain/backend/.venv/bin/activate

GUNICORN_VERSION="23.0.0"

# Vérification de l'installation de Gunicorn avec la bonne version
if ! python -c "import gunicorn; assert gunicorn.__version__ == '$GUNICORN_VERSION'" &> /dev/null; then
    echo "Gunicorn version $GUNICORN_VERSION non détectée, installation en cours..."
    pip install gunicorn=="$GUNICORN_VERSION"
    echo "Gunicorn version $GUNICORN_VERSION installée avec succès."
else
    echo "Gunicorn version $GUNICORN_VERSION est déjà installée."
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
