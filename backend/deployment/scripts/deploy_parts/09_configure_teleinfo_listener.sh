#!/bin/bash
# Configuration de Teleinfo Listener
sudo cp /home/admin/housebrain/backend/deployment/teleinfo-listener/teleinfo-listener.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable teleinfo-listener.service
sudo systemctl start teleinfo-listener.service

# Vérification du service
if systemctl is-active --quiet teleinfo-listener.service; then
    echo "Teleinfo Listener est actif."
else
    echo "Teleinfo Listener n'a pas démarré correctement."
fi
