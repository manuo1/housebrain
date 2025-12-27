#!/bin/bash
# Configuration de Bluetooth Listener
source /home/admin/housebrain/backend/.venv/bin/activate

BLEAK_VERSION="0.22.3"

# Vérification de l'installation de Bleak avec la bonne version
if ! python -c "import bleak; assert bleak.__version__ == '$BLEAK_VERSION'" &> /dev/null; then
    echo "Bleak version $BLEAK_VERSION non détectée, installation en cours..."
    pip install bleak=="$BLEAK_VERSION"
    echo "Bleak version $BLEAK_VERSION installée avec succès."
else
    echo "Bleak version $BLEAK_VERSION est déjà installée."
fi

sudo cp /home/admin/housebrain/backend/deployment/bluetooth-listener/bluetooth-listener.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable bluetooth-listener.service
sudo systemctl start bluetooth-listener.service

# Vérification du service
if systemctl is-active --quiet bluetooth-listener.service; then
    echo "Bluetooth Listener est actif."
else
    echo "Bluetooth Listener n'a pas démarré correctement."
fi
