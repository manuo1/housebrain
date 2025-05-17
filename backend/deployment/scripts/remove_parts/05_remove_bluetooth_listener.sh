#!/bin/bash
# Désinstallation de Bluetooth Listener

# Arrêt et désactivation du service
sudo systemctl stop bluetooth-listener.service
sudo systemctl disable bluetooth-listener.service

# Suppression du fichier service
sudo rm -f /etc/systemd/system/bluetooth-listener.service
sudo systemctl daemon-reload

# Activation de l'environnement virtuel et désinstallation de Bleak
source /home/admin/housebrain/backend/.venv/bin/activate
pip uninstall -y bleak

echo "Bluetooth Listener et Bleak désinstallés avec succès."
