#!/bin/bash
# Configuration de journald en logs persistants (survit aux reboots)
# Reproduit la config manuelle faite précédemment sur le Pi pour l'investigation
# des freezes aléatoires (I2C/thermique), désormais scriptée et rejouable.
#
# Idempotent : peut être rejoué sans dupliquer/casser la config existante.

JOURNALD_CONF="/etc/systemd/journald.conf"
CHANGED=0

set_journald_option() {
    local key="$1"
    local value="$2"
    if grep -qE "^${key}=${value}$" "$JOURNALD_CONF"; then
        return
    fi
    if grep -qE "^#?${key}=" "$JOURNALD_CONF"; then
        sudo sed -i -E "s/^#?${key}=.*/${key}=${value}/" "$JOURNALD_CONF"
    else
        echo "${key}=${value}" | sudo tee -a "$JOURNALD_CONF" > /dev/null
    fi
    echo "journald: ${key}=${value} appliqué."
    CHANGED=1
}

echo "=== Configuration journald persistant ==="

set_journald_option "Storage" "persistent"
set_journald_option "SystemMaxUse" "100M"
set_journald_option "SystemMaxFileSize" "20M"
set_journald_option "Compress" "yes"

# Répertoire de logs persistants
if [ ! -d /var/log/journal ]; then
    echo "Création de /var/log/journal..."
    sudo mkdir -p /var/log/journal
    sudo systemd-tmpfiles --create --prefix /var/log/journal
    CHANGED=1
else
    echo "/var/log/journal existe déjà."
fi

if [ "$CHANGED" = "1" ]; then
    echo "Redémarrage de systemd-journald pour appliquer la config..."
    sudo systemctl restart systemd-journald
else
    echo "Aucun changement, journald déjà configuré en persistant."
fi

if systemctl is-active --quiet systemd-journald; then
    echo "journald actif."
else
    echo "ATTENTION : journald n'a pas redémarré correctement."
fi
