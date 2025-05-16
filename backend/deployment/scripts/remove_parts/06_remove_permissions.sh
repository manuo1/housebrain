#!/bin/bash
# Réinitialisation des permissions et suppression des configurations

sudo usermod -R admin www-data
sudo chmod 755 /home/admin
sudo chown -R admin:admin /home/admin/housebrain

echo "Permissions réinitialisées."
