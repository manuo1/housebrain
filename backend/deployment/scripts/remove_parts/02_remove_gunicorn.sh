#!/bin/bash
# Désinstallation de Gunicorn

echo "Arrêt et suppression de Gunicorn..."

# Arrêter et désactiver le service
sudo systemctl stop gunicorn
sudo systemctl disable gunicorn

# Supprimer les fichiers de service
sudo rm -f /etc/systemd/system/gunicorn.service
sudo rm -f /etc/systemd/system/gunicorn.socket
sudo systemctl daemon-reload

# Supprimer Gunicorn du venv
source /home/admin/housebrain/backend/.venv/bin/activate
pip uninstall -y gunicorn
deactivate

echo "Gunicorn désinstallé avec succès."
