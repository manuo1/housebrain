#!/bin/bash
# Configuration de Bluetooth Listener (service systemd)
# bleak est désormais dans requirements.txt (installé par 04_configure_venv.sh) —
# pas de check de version en dur ici, pour éviter toute divergence avec la source de vérité.

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
