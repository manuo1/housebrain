```bash
# Arrêter le service Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx
# Désinstaller Nginx
sudo apt remove nginx -y
sudo apt purge nginx -y
# Supprimer les dépendances inutilisées
sudo apt autoremove --purge -y
# Supprimer les fichiers de configuration restants
sudo rm -rf /etc/nginx
sudo rm -rf /var/log/nginx
sudo rm -rf /var/www/html
# sudo find / -name "*nginx*" -exec rm -rf {} \;
sudo find / -name "*nginx*" -exec rm -rf {} \;
```