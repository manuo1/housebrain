#!/bin/bash
# Configuration des permissions
sudo usermod -aG admin www-data
sudo chmod 750 /home/admin
sudo chown -R admin:www-data /home/admin/housebrain
chmod 664 /home/admin/housebrain/backend/db.sqlite3
chmod 775 /home/admin/housebrain/backend
mkdir -p /home/admin/housebrain/backend/media
sudo chmod 775 /home/admin/housebrain/backend/media

echo "Permissions configurées avec succès."
