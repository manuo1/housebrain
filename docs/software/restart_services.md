# Redémarrage des services HouseBrain

## Services principaux
```bash
# Recharger systemd pour prendre en compte les modifications
sudo systemctl daemon-reload

# Redémarrer Nginx
sudo systemctl restart nginx

# Redémarrer Gunicorn
sudo systemctl restart gunicorn

# Redémarrer Teleinfo Listener
sudo systemctl restart teleinfo-listener

# Redémarrer Bluetooth Listener
sudo systemctl restart bluetooth-listener

# Redémarrer le Scheduler (tâches périodiques)
sudo systemctl restart housebrain-periodic.timer
```

---

## Vérification des statuts
```bash
# Vérifier l'état de tous les services
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status teleinfo-listener
sudo systemctl status bluetooth-listener
sudo systemctl status housebrain-periodic.timer

# Voir la prochaine exécution du timer
systemctl list-timers housebrain-periodic.timer
```

---

## Arrêt / Démarrage individuel
```bash
# Arrêter un service
sudo systemctl stop <nom-du-service>

# Démarrer un service
sudo systemctl start <nom-du-service>

# Désactiver un service (ne démarre plus au boot)
sudo systemctl disable <nom-du-service>

# Activer un service (démarre au boot)
sudo systemctl enable <nom-du-service>
```

---

## Redémarrage complet de l'application
```bash
# Redémarrer tous les services HouseBrain
sudo systemctl restart nginx gunicorn teleinfo-listener bluetooth-listener housebrain-periodic.timer

# Vérifier tous les statuts
sudo systemctl status nginx gunicorn teleinfo-listener bluetooth-listener housebrain-periodic.timer --no-pager
```
