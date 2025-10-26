# Configuration HTTPS avec Let's Encrypt

Ce guide détaille la procédure de mise en place du certificat SSL/TLS avec Let's Encrypt pour sécuriser l'application HouseBrain.

## 📋 Prérequis

- Raspberry Pi accessible depuis Internet
- Nom de domaine configuré (ex: `votredomaine.fr`)
- Ports 80 et 443 redirigés vers le Raspberry Pi via la box Internet
- Nginx installé et configuré
- Django tournant avec Gunicorn

## 🌐 1. Configuration DNS

### Chez votre registrar (OVH, Gandi, etc.)

Créez un enregistrement DNS de type **A** :

```
housebrain.votredomaine.fr  →  Votre_IP_Publique
```

**Vérification :**
```bash
# Testez la résolution DNS
nslookup housebrain.votredomaine.fr
```

## 🔧 2. Redirection des ports (Box Internet)

Configurez les redirections NAT/PAT suivantes :

| Port externe | Port interne | Protocole | Usage |
|-------------|--------------|-----------|-------|
| 80 | 80 | TCP | HTTP (validation Let's Encrypt) |
| 443 | 443 | TCP | HTTPS (application) |

**Commentaire suggéré :** `HTTPS - Caddy → Django (housebrain)`

## 🔐 3. Installation de Certbot

Certbot est le client officiel Let's Encrypt pour obtenir et renouveler automatiquement les certificats SSL.

```bash
# Mise à jour des paquets
sudo apt update

# Installation de Certbot avec le plugin Nginx
sudo apt install certbot python3-certbot-nginx -y

# Vérification
certbot --version
```

## 📝 4. Préparation de la configuration Nginx

**Avant d'obtenir le certificat**, assurez-vous que votre configuration Nginx contient le bon `server_name` :

```bash
# Éditez votre configuration Nginx
sudo nano /etc/nginx/sites-available/housebrain
```

**Modifiez la ligne `server_name` :**

```nginx
server {
    listen 80;
    server_name housebrain.votredomaine.fr;  # ⚠️ Utilisez votre vrai domaine

    # ... reste de la configuration
}
```

**Testez et rechargez :**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🎉 5. Obtention du certificat SSL

Lancez Certbot en mode automatique :

```bash
sudo certbot --nginx -d housebrain.votredomaine.fr
```

**Répondez aux questions :**

1. **Email :** Votre adresse email (pour les alertes d'expiration)
2. **Conditions d'utilisation :** Acceptez (`Y`)
3. **Newsletter EFF :** À votre convenance (`Y` ou `N`)

**Certbot va automatiquement :**
- ✅ Valider votre domaine via HTTP-01 challenge
- ✅ Obtenir le certificat Let's Encrypt
- ✅ Modifier votre configuration Nginx pour activer HTTPS
- ✅ Configurer la redirection HTTP → HTTPS

## ✅ 6. Vérification de la configuration

### Configuration Nginx générée

Certbot ajoute automatiquement ces sections :

```nginx
server {
    server_name housebrain.votredomaine.fr;

    # ... votre configuration existante ...

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/housebrain.votredomaine.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/housebrain.votredomaine.fr/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = housebrain.votredomaine.fr) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name housebrain.votredomaine.fr;
    return 404;
}
```

### Test du renouvellement automatique

```bash
# Simulation (dry-run) du renouvellement
sudo certbot renew --dry-run
```

**Résultat attendu :**
```
Congratulations, all simulated renewals succeeded
```

### Vérification du timer systemd

Le renouvellement automatique est géré par un timer systemd :

```bash
sudo systemctl status certbot.timer
```

**Le certificat se renouvelle automatiquement tous les 60 jours** (valide 90 jours).

## 🐍 7. Configuration Django (Production)

Ajoutez les paramètres de sécurité HTTPS dans `backend/core/settings/production.py` :

```python
# ============================================
# SÉCURITÉ HTTPS
# ============================================

# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security) - 1 an
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**Rechargez Gunicorn :**

```bash
sudo systemctl restart gunicorn
```

## 🌐 8. Tests finaux

### Test dans le navigateur

1. **Accès HTTPS :**
   ```
   https://housebrain.votredomaine.fr
   ```
   ✅ Vous devez voir le cadenas vert 🔒

2. **Redirection HTTP → HTTPS :**
   ```
   http://housebrain.votredomaine.fr
   ```
   ✅ Doit rediriger automatiquement vers HTTPS

### Vérification du certificat

Cliquez sur le cadenas 🔒 dans la barre d'adresse :
- **Émis par :** Let's Encrypt
- **Valide pendant :** 90 jours (renouvelé automatiquement)

### Test du grade SSL (optionnel)

Analysez votre configuration SSL :
```
https://www.ssllabs.com/ssltest/analyze.html?d=housebrain.votredomaine.fr
```

**Objectif :** Note **A** ou **A+**

## 🔄 Maintenance

### Vérification des certificats

```bash
# Liste les certificats installés
sudo certbot certificates
```

### Renouvellement manuel (si nécessaire)

```bash
# Force le renouvellement
sudo certbot renew

# Recharge Nginx après renouvellement
sudo systemctl reload nginx
```

### Logs Certbot

```bash
# Consulter les logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

## 🛡️ Sécurité supplémentaire (optionnel)

### Headers de sécurité additionnels

Ajoutez dans votre configuration Nginx (bloc `server` HTTPS) :

```nginx
# Headers de sécurité
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Content Security Policy (CSP)

Pour une sécurité renforcée contre XSS :

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

⚠️ **Attention :** Testez bien la CSP, elle peut bloquer certaines ressources.

## 🐛 Troubleshooting

### Erreur : "Failed to obtain certificate"

**Cause :** Le port 80 n'est pas accessible depuis Internet.

**Solution :**
```bash
# Vérifiez que Nginx écoute sur le port 80
sudo netstat -tlnp | grep :80

# Testez l'accès externe
curl -I http://housebrain.votredomaine.fr
```

### Erreur : "Connection refused" sur le port 443

**Cause :** Le port 443 n'est pas redirigé correctement.

**Solution :**
- Vérifiez la redirection de port sur votre box Internet
- Vérifiez que Nginx écoute bien sur 443 :
  ```bash
  sudo ss -tlnp | grep :443
  ```

### Django : "Bad Request (400)"

**Cause :** Votre domaine n'est pas dans `ALLOWED_HOSTS`.

**Solution :** Ajoutez-le dans votre `.env` :
```bash
DOMAINS=housebrain.votredomaine.fr
```

### Certificat non renouvelé automatiquement

**Vérification :**
```bash
# Vérifiez le timer
sudo systemctl status certbot.timer

# Si inactif, activez-le
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 📚 Ressources

- [Documentation Let's Encrypt](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)

## 📝 Notes importantes

- ⚠️ **Ne commitez JAMAIS vos clés privées** (`/etc/letsencrypt/` doit rester sur le serveur)
- 🔄 Les certificats Let's Encrypt sont valides **90 jours** et se renouvellent automatiquement
- 📧 Utilisez une **adresse email valide** pour recevoir les alertes d'expiration
- 🔐 En production, **HTTPS doit TOUJOURS être activé** (pas en développement local)

---

**Date de création :** Octobre 2025
**Dernière mise à jour :** Octobre 2025
**Testé sur :** Raspberry Pi 4 - Raspbian Bookworm - Nginx 1.22 - Django 5.2
