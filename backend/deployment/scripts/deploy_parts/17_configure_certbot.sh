#!/bin/bash
# Configuration Certbot / HTTPS (Let's Encrypt) pour Nginx
#
# Idempotent, à rejouer à chaque déploiement : 03_configure_nginx.sh réécrit
# systématiquement la conf nginx HTTP de base depuis le repo (source de vérité).
# Ce script réapplique ensuite le bloc SSL géré par Certbot juste après, pour que
# la config live ne diverge plus jamais silencieusement du repo (c'était le cas
# jusqu'ici : le bloc SSL ajouté à la main par Certbot était perdu à chaque
# déploiement sans que personne ne le remarque).
#
# Nécessite dans .env :
#   DOMAINS=housebrain.exemple.fr[,autre.domaine.fr]
#   CERTBOT_EMAIL=admin@exemple.fr
# Si DOMAINS n'est pas configuré (valeur d'exemple laissée telle quelle), ce module
# est ignoré : le déploiement reste utilisable en HTTP seul (accès LAN uniquement).

cd /home/admin/housebrain/backend
source .env 2>/dev/null || true

if [ -z "$DOMAINS" ] || [ "$DOMAINS" = "ma-super-app.fr,www.ma-super-app.fr" ]; then
    echo "DOMAINS non configuré dans .env, HTTPS/Certbot ignoré (accès HTTP/LAN uniquement)."
    exit 0
fi

if [ -z "$CERTBOT_EMAIL" ]; then
    echo "ERREUR : CERTBOT_EMAIL absent de .env, requis par Let's Encrypt (rappels d'expiration)."
    echo "Ajoute CERTBOT_EMAIL=ton@email.fr dans .env et relance ce script."
    exit 1
fi

# Installation de Certbot + plugin Nginx
if ! command -v certbot &> /dev/null; then
    echo "Certbot non détecté, installation..."
    sudo apt-get install -y certbot python3-certbot-nginx
else
    echo "Certbot déjà installé."
fi

# Construction des arguments -d pour chaque domaine (DOMAINS séparés par des virgules)
DOMAIN_ARGS=()
IFS=',' read -ra DOMAIN_LIST <<< "$DOMAINS"
for d in "${DOMAIN_LIST[@]}"; do
    DOMAIN_ARGS+=("-d" "$d")
done

# Obtention/renouvellement + (ré)application du bloc SSL dans nginx.
# --keep-until-expiring : ne redemande pas de certificat si l'existant est encore valide.
# Rejouable sans risque à chaque déploiement.
sudo certbot --nginx "${DOMAIN_ARGS[@]}" \
    --non-interactive --agree-tos \
    -m "$CERTBOT_EMAIL" \
    --redirect \
    --keep-until-expiring

# Le paquet certbot installe et active normalement son propre timer de renouvellement
if sudo systemctl is-active --quiet certbot.timer; then
    echo "Renouvellement automatique Certbot actif (certbot.timer)."
else
    echo "ATTENTION : certbot.timer n'est pas actif, le renouvellement automatique ne fonctionnera pas."
fi

sudo nginx -t && sudo systemctl reload nginx
