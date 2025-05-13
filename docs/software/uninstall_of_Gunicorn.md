```bash
# Arrêter le service
sudo systemctl stop gunicorn
# Le désactiver pour qu'il ne démarre plus au boot
sudo systemctl disable gunicorn
# Supprimer le fichier de configuration
sudo rm /etc/systemd/system/gunicorn.service
# Recharger les services
sudo systemctl daemon-reload
# Pour être sûr qu'il n'y a plus de processus Gunicorn actif
sudo pkill gunicorn
# Supprimer les sockets
sudo rm /run/gunicorn.sock

```