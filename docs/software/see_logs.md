##  **Voir les logs en temps réel :**

### **Nginx :**
Affiche les logs du serveur web Nginx.
```bash
sudo journalctl -u nginx -f
```

---

### **Gunicorn :**
Affiche les logs du serveur d'application Gunicorn.
```bash
sudo journalctl -u gunicorn -f
```

---

### **Teleinfo Listener :**
Affiche les logs du listener Teleinfo.
```bash
sudo journalctl -u teleinfo-listener -f
```

---

### **Bluetooth Listener :**
Affiche les logs du listener Bluetooth.
```bash
sudo journalctl -u bluetooth-listener -f
```

---

### **Redis :**
Affiche les logs du serveur Redis.
```bash
sudo journalctl -u redis-server -f
```

---

### **Scheduler (tâches périodiques) :**
Affiche les logs du Scheduler.
```bash
sudo journalctl -u housebrain-periodic -f
```

**Voir la prochaine exécution du timer** :
```bash
systemctl list-timers housebrain-periodic.timer
```
