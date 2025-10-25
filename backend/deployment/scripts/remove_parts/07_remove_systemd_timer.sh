#!/bin/bash
# Suppression du systemd timer pour les tâches périodiques

set -e

SERVICE_FILE="housebrain-periodic.service"
TIMER_FILE="housebrain-periodic.timer"

echo "Suppression du systemd timer..."

# Arrêter et désactiver le timer
if systemctl is-active --quiet ${TIMER_FILE}; then
    sudo systemctl stop ${TIMER_FILE}
    echo "✓ Timer arrêté"
fi

if systemctl is-enabled --quiet ${TIMER_FILE} 2>/dev/null; then
    sudo systemctl disable ${TIMER_FILE}
    echo "✓ Timer désactivé"
fi

# Supprimer les fichiers systemd
if [ -f "/etc/systemd/system/${SERVICE_FILE}" ]; then
    sudo rm /etc/systemd/system/${SERVICE_FILE}
    echo "✓ Service supprimé"
fi

if [ -f "/etc/systemd/system/${TIMER_FILE}" ]; then
    sudo rm /etc/systemd/system/${TIMER_FILE}
    echo "✓ Timer supprimé"
fi

# Recharger systemd
sudo systemctl daemon-reload
sudo systemctl reset-failed 2>/dev/null || true

echo "✓ Systemd timer complètement supprimé"
