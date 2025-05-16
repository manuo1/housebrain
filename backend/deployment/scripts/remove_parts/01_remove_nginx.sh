#!/bin/bash
# Désinstallation de Nginx

sudo systemctl stop nginx
sudo systemctl disable nginx
sudo apt-get remove --purge -y nginx nginx-common
sudo apt-get autoremove -y
sudo rm -rf /etc/nginx/sites-available/housebrain
sudo rm -rf /etc/nginx/sites-enabled/housebrain

echo "Nginx désinstallé avec succès."
