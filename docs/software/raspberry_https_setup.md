# HTTPS avec Let's Encrypt

Depuis le module `17_configure_certbot.sh`, l'obtention et le renouvellement du
certificat HTTPS sont **automatiques** : ce document sert de référence sur ce qui
se passe sous le capot, les prérequis que tu dois toi-même mettre en place (DNS,
box), et du troubleshooting si quelque chose ne marche pas comme prévu.

## Prérequis (à faire toi-même, pas automatisable)

- Nom de domaine configuré chez ton registrar, avec un enregistrement DNS de type
  **A** pointant vers ton IP publique :
  ```
  housebrain.tondomaine.fr  →  Ton_IP_Publique
  ```
  Vérification : `nslookup housebrain.tondomaine.fr`
- Redirections de ports sur ta box : port externe 80 → Pi:80 (validation Let's
  Encrypt), port externe 443 → Pi:443 (application HTTPS)

## Configuration à renseigner

Dans `/home/admin/housebrain/backend/.env` :

```bash
DOMAINS=housebrain.tondomaine.fr
CERTBOT_EMAIL=ton@email.fr
```

`CERTBOT_EMAIL` sert uniquement aux alertes d'expiration envoyées par Let's
Encrypt.

## Ce que fait l'automatisation

À chaque déploiement ou mise à jour (`deploy.sh` / `update.sh`), le module
`17_configure_certbot.sh` :
1. Installe Certbot + le plugin Nginx s'ils sont absents
2. Obtient le certificat (ou ne fait rien s'il est déjà valide et loin de
   l'expiration — `--keep-until-expiring`)
3. Applique/réapplique le bloc HTTPS dans la config Nginx (`listen 443 ssl`,
   chemins des certs) et la redirection HTTP → HTTPS
4. Vérifie que `certbot.timer` (renouvellement automatique) est actif

C'est rejoué à **chaque** déploiement, pas seulement la première fois : ça évite
que la config Nginx générée par `03_configure_nginx.sh` (HTTP simple) écrase le
bloc HTTPS ajouté par Certbot, comme c'était le cas avant cette automatisation.

Si `DOMAINS` n'est pas configuré, ce module est simplement ignoré (l'application
reste utilisable en HTTP sur le réseau local).

## Configuration Django associée

Les réglages de sécurité HTTPS sont déjà en place dans
`backend/core/settings/production.py` (rien à faire) :

```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Vérifications manuelles

```bash
# Certificats installés
sudo certbot certificates

# Simulation de renouvellement (ne modifie rien)
sudo certbot renew --dry-run

# Le renouvellement automatique est actif ?
sudo systemctl status certbot.timer
```

Le certificat Let's Encrypt est valide 90 jours ; `certbot.timer` tente un
renouvellement deux fois par jour et ne renouvelle réellement que dans les 30
derniers jours avant expiration.

## Tests dans le navigateur

- `https://housebrain.tondomaine.fr` → cadenas 🔒, émis par Let's Encrypt
- `http://housebrain.tondomaine.fr` → doit rediriger automatiquement vers HTTPS
- Optionnel, note de qualité SSL : https://www.ssllabs.com/ssltest/analyze.html?d=housebrain.tondomaine.fr

## Dépannage

### "Failed to obtain certificate"
Le port 80 n'est probablement pas accessible depuis Internet (redirection box
manquante, ou Nginx pas démarré). Vérifie :
```bash
sudo ss -tlnp | grep :80
curl -I http://housebrain.tondomaine.fr
```

### "Connection refused" sur le port 443
Vérifie la redirection de port 443 sur la box, et que Nginx écoute bien dessus :
```bash
sudo ss -tlnp | grep :443
```

### Django : "Bad Request (400)"
Le domaine n'est pas dans `DOMAINS`/`ALLOWED_HOSTS`. Vérifie `.env` :
```bash
DOMAINS=housebrain.tondomaine.fr
```

### Le certificat ne se renouvelle pas automatiquement
```bash
sudo systemctl status certbot.timer
# Si inactif :
sudo systemctl enable --now certbot.timer
```

### Logs Certbot
```bash
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

## Intervention manuelle (cas de debug seulement)

Si tu as besoin de relancer Certbot toi-même en dehors du script (debug) :
```bash
sudo certbot --nginx -d housebrain.tondomaine.fr --non-interactive --agree-tos -m ton@email.fr --redirect --keep-until-expiring
```
C'est exactement la commande utilisée par `17_configure_certbot.sh`.

## Sécurité supplémentaire (optionnel, pas géré par les scripts)

Headers additionnels à ajouter à la main dans le bloc `server` HTTPS de Nginx si
tu veux aller plus loin :
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```
⚠️ Ces lignes seront perdues au prochain déploiement (`03_configure_nginx.sh`
réécrit la config depuis le repo) — si tu veux les garder, ajoute-les plutôt dans
`backend/deployment/nginx/housebrain` versionné dans le repo.

## Ressources

- [Documentation Let's Encrypt](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

---

Dernière mise à jour : Juillet 2026
