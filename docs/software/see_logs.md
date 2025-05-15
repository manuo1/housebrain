```bash
# Voir les logs de Gunicorn
sudo journalctl -u gunicorn --since "5 minutes ago"

# Voir les logs d'erreur de Nginx
sudo tail -f /var/log/nginx/error.log
```