#!/bin/bash
# Désinstallation de Teleinfo Listener

sudo systemctl stop teleinfo-listener.service
sudo systemctl disable teleinfo-listener.service
sudo rm -f /etc/systemd/system/teleinfo-listener.service
sudo systemctl daemon-reload

echo "Teleinfo Listener désinstallé avec succès."
