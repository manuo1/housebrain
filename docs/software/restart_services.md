```bash
# Recharger systemd pour prendre en compte les modifications du fichier service
sudo systemctl daemon-reload

# Redémarrer Gunicorn
sudo systemctl restart gunicorn

# Redémarrer Nginx
sudo systemctl restart nginx

# Vérifier l'état de Gunicorn
sudo systemctl status gunicorn

# Vérifier l'état de Nginx
sudo systemctl status nginx
```