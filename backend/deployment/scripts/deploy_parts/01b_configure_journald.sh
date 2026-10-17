#!/bin/bash
# Configure journald so logs are persistent (they survive reboots and freezes).
#
# Raspberry Pi OS ships /usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf
# (Storage=volatile). Drop-ins are applied after journald.conf, so editing
# journald.conf alone has NO effect: logs stay in RAM (/run/log/journal).
# We therefore install our own drop-in in /etc (never overwritten by apt),
# named 99-* so it sorts after every vendor drop-in, and we verify the
# EFFECTIVE configuration rather than trusting the file we wrote.
#
# Idempotent: safe to replay. Exits 1 if journald is still not persistent,
# so a silent regression (e.g. after a system upgrade) is caught on the next update.

DROPIN_DIR="/etc/systemd/journald.conf.d"
DROPIN_FILE="${DROPIN_DIR}/99-housebrain.conf"
DESIRED_CONTENT="[Journal]
Storage=persistent
SystemMaxUse=100M
SystemMaxFileSize=20M
MaxRetentionSec=30day
Compress=yes"
CHANGED=0

echo "=== Configuration journald persistant ==="

sudo mkdir -p "$DROPIN_DIR"

if [ "$(cat "$DROPIN_FILE" 2>/dev/null)" != "$DESIRED_CONTENT" ]; then
    echo "$DESIRED_CONTENT" | sudo tee "$DROPIN_FILE" > /dev/null
    echo "journald: drop-in ${DROPIN_FILE} écrit."
    CHANGED=1
else
    echo "journald: drop-in ${DROPIN_FILE} déjà à jour."
fi

# Persistent log directory
if [ ! -d /var/log/journal ]; then
    echo "Création de /var/log/journal..."
    sudo mkdir -p /var/log/journal
    sudo systemd-tmpfiles --create --prefix /var/log/journal
    CHANGED=1
fi

if [ "$CHANGED" = "1" ]; then
    echo "Redémarrage de systemd-journald pour appliquer la config..."
    sudo systemctl restart systemd-journald
    # Move what is still in the RAM journal (/run) to the persistent one
    sudo journalctl --flush
fi

# Verification on the effective config (all files merged), last Storage= wins
EFFECTIVE_STORAGE=$(systemd-analyze cat-config systemd/journald.conf 2>/dev/null \
    | grep -E '^Storage=' | tail -1 | cut -d= -f2)

if [ "$EFFECTIVE_STORAGE" != "persistent" ]; then
    echo "ERREUR : Storage effectif = '${EFFECTIVE_STORAGE}' (attendu : persistent)."
    echo "Un autre fichier de conf passe après ${DROPIN_FILE} :"
    echo "  systemd-analyze cat-config systemd/journald.conf | grep -nE '^(#|Storage=)'"
    exit 1
fi

if ! ls /var/log/journal/*/system.journal > /dev/null 2>&1; then
    echo "ERREUR : aucun system.journal sous /var/log/journal (journald écrit encore en RAM)."
    exit 1
fi

if ! systemctl is-active --quiet systemd-journald; then
    echo "ERREUR : journald n'est pas actif."
    exit 1
fi

echo "journald persistant : OK (Storage effectif = persistent)."
