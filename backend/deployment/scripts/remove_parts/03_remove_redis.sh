#!/bin/bash
# Désinstallation de Redis

sudo systemctl stop redis-server
sudo systemctl disable redis-server
sudo apt-get remove --purge -y redis-server
sudo apt-get autoremove -y
sudo rm -rf /var/lib/redis

echo "Redis désinstallé avec succès."
