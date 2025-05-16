#!/bin/bash
# Désinstallation de Gunicorn

sudo systemctl stop gunicorn
sudo systemctl disable gunicorn
sudo rm -f /etc/systemd/system/gunicorn.service
sudo rm -f /etc/systemd/system/gunicorn.socket
sudo systemctl daemon-reload
sudo apt-get remove --purge -y gunicorn
sudo apt-get autoremove -y

echo "Gunicorn désinstallé avec succès."
