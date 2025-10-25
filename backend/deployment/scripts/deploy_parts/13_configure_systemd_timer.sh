#!/bin/bash
# Configuration du systemd timer pour les tâches périodiques Django

set -e

SYSTEMD_DIR="/home/admin/housebrain/backend/deployment/systemd-timers"
SERVICE_FILE="housebrain-periodic.service"
TIMER_FILE="housebrain-periodic.timer"

echo "Installation du systemd timer pour les tâches périodiques..."

# Vérifier que les fichiers source existent
if [ ! -f "${SYSTEMD_DIR}/${SERVICE_FILE}" ]; then
    echo "Erreur: ${SYSTEMD_DIR}/${SERVICE_FILE} introuvable"
    exit 1
fi

if [ ! -f "${SYSTEMD_DIR}/${TIMER_FILE}" ]; then
    echo "Erreur: ${SYSTEMD_DIR}/${TIMER_FILE} introuvable"
    exit 1
fi

# Copier les fichiers systemd
sudo cp "${SYSTEMD_DIR}/${SERVICE_FILE}" /etc/systemd/system/
sudo cp "${SYSTEMD_DIR}/${TIMER_FILE}" /etc/systemd/system/

# Définir les permissions
sudo chmod 644 /etc/systemd/system/${SERVICE_FILE}
sudo chmod 644 /etc/systemd/system/${TIMER_FILE}

# Recharger systemd
sudo systemctl daemon-reload

# Activer et démarrer le timer
sudo systemctl enable ${TIMER_FILE}
sudo systemctl start ${TIMER_FILE}

echo "✓ Timer systemd configuré et démarré"
echo ""
echo "Vérification du statut:"
sudo systemctl status ${TIMER_FILE} --no-pager || true
echo ""
echo "Prochaine exécution:"
systemctl list-timers ${TIMER_FILE} --no-pager || true
