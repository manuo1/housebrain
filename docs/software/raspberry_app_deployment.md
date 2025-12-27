# Déploiement de HouseBrain sur Raspberry Pi

## Prérequis

### Matériel nécessaire
- Raspberry Pi 3 B+ (ou supérieur)
- Clé USB avec Raspberry Pi OS Lite (64-bit)
- Alimentation 5V 2.5A minimum
- Carte lecture Téléinfo (compteur Linky) - voir `docs/hardware/teleinfo_branchement.md`
- Carte pilotage fil pilote (MCP23017 via I2C) - documentation en cours

### Réseau
- IP fixe publique (recommandé pour stabilité du nom de domaine)
- Nom de domaine configuré pointant vers votre IP publique
- Ports 80 et 443 ouverts sur votre Box Internet
- Accès SSH au Raspberry Pi

---

## Configuration matérielle

### 1. Activer le Port Série (lecture Téléinfo)

Indispensable pour la lecture des données du compteur Linky.

```bash
sudo raspi-config
```

Navigation :
- `3 Interface Options` > Configure connections to peripherals
- `I6 Serial Port` > Enable/disable shell messages on the serial connection

Réponses :
- Would you like a login shell to be accessible over serial? > **No**
- Would you like the serial port hardware to be enabled? > **Yes**

Résultat attendu :
```
The serial login shell is disabled
The serial interface is enabled
```

Redémarrer le Raspberry :
```bash
sudo reboot
```

---

### 2. Activer le Port I2C (pilotage MCP23017)

Indispensable pour piloter les relais de chauffage via le MCP23017.

```bash
sudo raspi-config
```

Navigation :
- `3 Interface Options` > Configure connections to peripherals
- `I5 I2C` > Enable/disable automatic loading of I2C kernel module

Réponses :
- Would you like the ARM I2C interface to be enabled? > **Yes**

---

### 3. Activer le Bluetooth (communication Bluetooth)

Indispensable pour les capteurs Bluetooth (utilisés par Bleak).

```bash
sudo raspi-config
```

Navigation :
- `3 Interface Options` > Configure connections to peripherals
- `I1 Bluetooth` > Enable/disable Bluetooth

Réponses :
- Would you like the Bluetooth to be enabled? > **Yes**

Vérifier que le service Bluetooth est actif :
```bash
sudo systemctl status bluetooth
```

---

## Déploiement initial

### 1. Connexion SSH

```bash
ssh admin@housebrain
```

### 2. Clonage du projet

```bash
cd /home/admin
git clone https://github.com/manuo1/housebrain.git
```

### 3. Exécution du script de déploiement

```bash
# Rendre le script exécutable
chmod +x /home/admin/housebrain/backend/deployment/scripts/deploy.sh

# Lancer le déploiement complet
/home/admin/housebrain/backend/deployment/scripts/deploy.sh
```

Le script va automatiquement :
1. Mettre à jour le système
2. Installer les dépendances (Python, Nginx, Redis)
3. Créer l'environnement virtuel Python
4. Installer Gunicorn et Django
5. Générer le fichier `.env` avec SECRET_KEY et IPs
6. Appliquer les migrations Django
7. Configurer les services systemd (Gunicorn, Teleinfo, Bluetooth)
8. Configurer le timer périodique (tâches planifiées)
9. Déployer un frontend fallback temporaire
10. Installer Node.js (si non présent)
11. Builder et déployer le frontend React

### 4. Création du superutilisateur Django

Pendant le déploiement, vous serez invité à créer un superutilisateur :
```
Username: admin
Email: votre-email@example.com
Password: ********
```

---

## Configuration HTTPS

IMPORTANT : Après le déploiement initial, configurez HTTPS avec Let's Encrypt.

Voir le guide détaillé : `docs/software/raspberry_https_setup.md`

Résumé des étapes :
1. Vérifier que votre nom de domaine pointe vers votre IP publique
2. Vérifier que les ports 80 et 443 sont ouverts sur votre Box
3. Installer Certbot et obtenir un certificat
4. Mettre à jour la variable `DOMAINS` dans `/home/admin/housebrain/backend/.env`

---

## Accès à l'application

Une fois HTTPS configuré :

- Interface web : `https://housebrain.emmanuel-oudot.fr/`
- Admin Django : `https://housebrain.emmanuel-oudot.fr/backend/admin/`
- API : `https://housebrain.emmanuel-oudot.fr/api/`

Remplacez `housebrain.emmanuel-oudot.fr` par votre propre domaine.

---

## Services déployés

| Service | Description | Vérification |
|---------|-------------|--------------|
| nginx | Serveur web (frontend + reverse proxy) | `sudo systemctl status nginx` |
| gunicorn | Serveur d'application Django | `sudo systemctl status gunicorn` |
| redis-server | Cache et pub/sub | `sudo systemctl status redis-server` |
| teleinfo-listener | Lecture compteur Linky | `sudo systemctl status teleinfo-listener` |
| bluetooth-listener | Communication Bluetooth | `sudo systemctl status bluetooth-listener` |
| housebrain-periodic.timer | Tâches périodiques (1 min) | `sudo systemctl status housebrain-periodic.timer` |

---

## Configuration avancée

### Variables d'environnement (.env)

Le fichier `/home/admin/housebrain/backend/.env` est généré automatiquement et contient :

```bash
SECRET_KEY=<généré-automatiquement>
DEBUG=False
ENVIRONMENT=production
SERIAL_PORT=/dev/ttyS0
LOCAL_IP=<détecté-automatiquement>
PUBLIC_IP=<détecté-automatiquement>
DOMAINS=<à-configurer-manuellement>  # Votre nom de domaine pour HTTPS
UNPLUGGED_MODE=False  # True = mode dev sans matériel
```

IMPORTANT : Après configuration HTTPS, modifiez la variable `DOMAINS` :
```bash
DOMAINS=housebrain.emmanuel-oudot.fr
```

### Mode développement sans matériel

Si vous développez sans Raspberry Pi physique, activez le mode "unplugged" :
```bash
UNPLUGGED_MODE=True
```
Cela désactive les interactions avec le GPIO, MCP23017, et le port série.

---

## Dépannage

### Vérifier les logs

```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Teleinfo
sudo journalctl -u teleinfo-listener -f

# Bluetooth
sudo journalctl -u bluetooth-listener -f
```

### Redémarrer les services

Voir le guide : `docs/software/restart_services.md`

---

## Documentation complémentaire

- `raspberry_app_update.md` - Mise à jour de l'application
- `raspberry_app_remove_full.md` - Désinstallation complète
- `raspberry_https_setup.md` - Configuration HTTPS (obligatoire)
- `raspberry_install.md` - Installation initiale du Raspberry Pi
- `see_logs.md` - Consultation des logs
- `restart_services.md` - Redémarrage des services

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
Testé sur : Raspberry Pi 3 B+ - Raspberry Pi OS Lite (64-bit) - Django 5.2
