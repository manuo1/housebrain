#!/bin/bash
# Préflight matériel Raspberry Pi OS : I2C (bus vers les MCP23017 des actionneurs),
# UART matériel (téléinfo Linky sur /dev/ttyS0), Bluetooth (capteurs BLE / BTHome).
#
# Idempotent : peut être rejoué à tout moment (install initiale ou update) sans effet
# de bord si tout est déjà configuré. S'arrête avec un message clair si un reboot est
# nécessaire pour que les changements prennent effet (I2C/UART nécessitent un reload
# du device tree, qui ne se fait qu'au boot).
#
# Suppose Raspberry Pi OS (raspi-config disponible). Sur un Debian nu, ce script
# échoue volontairement plutôt que de deviner une config.

set -e

TARGET_USER="admin"
REBOOT_REQUIRED=0

echo "=== [00] Préflight matériel ==="

if ! command -v raspi-config &> /dev/null; then
    echo "ERREUR : raspi-config introuvable."
    echo "Ce script suppose Raspberry Pi OS. Sur un autre OS, il faut adapter"
    echo "l'activation I2C/UART (édition manuelle de config.txt) avant de continuer."
    exit 1
fi

# --- I2C : bus vers les MCP23017 (actuators) ---
echo "--- I2C ---"
if [ "$(sudo raspi-config nonint get_i2c)" = "1" ]; then
    echo "I2C désactivé, activation..."
    sudo raspi-config nonint do_i2c 0
    REBOOT_REQUIRED=1
else
    echo "I2C déjà activé."
fi

if [ ! -e /dev/i2c-1 ]; then
    echo "I2C activé en config mais /dev/i2c-1 absent : le kernel n'a pas encore chargé le driver."
    REBOOT_REQUIRED=1
fi

# --- UART matériel : téléinfo Linky sur /dev/ttyS0 ---
# Note : le service teleinfo-listener attend /dev/ttyS0 (mini-UART), pas /dev/ttyAMA0.
# Le Bluetooth reste donc sur le PL011 par défaut, pas de dtoverlay=disable-bt nécessaire ici.
echo "--- UART ---"
if [ "$(sudo raspi-config nonint get_serial_hw)" = "1" ]; then
    echo "UART matériel désactivé, activation..."
    sudo raspi-config nonint do_serial_hw 0
    REBOOT_REQUIRED=1
else
    echo "UART matériel déjà activé."
fi

if [ "$(sudo raspi-config nonint get_serial_cons)" = "0" ]; then
    echo "Console série (login shell) active sur l'UART, désactivation (nécessaire pour libérer ttyS0)..."
    sudo raspi-config nonint do_serial_cons 1
    REBOOT_REQUIRED=1
else
    echo "Console série déjà désactivée."
fi

# --- Bluetooth : capteurs BLE (scan passif BTHome, pas d'appairage) ---
echo "--- Bluetooth ---"
if ! dpkg -l | grep -q '^ii  bluez '; then
    echo "BlueZ absent, installation..."
    sudo apt-get install -y bluez
else
    echo "BlueZ déjà installé."
fi

if ! systemctl is-active --quiet bluetooth; then
    echo "Activation du service bluetooth..."
    sudo systemctl enable --now bluetooth
else
    echo "Service bluetooth déjà actif."
fi

# --- Groupes utilisateur : accès non-root aux périphériques ---
echo "--- Groupes ---"
for grp in i2c dialout bluetooth; do
    if ! id -nG "$TARGET_USER" | grep -qw "$grp"; then
        echo "Ajout de $TARGET_USER au groupe $grp..."
        sudo usermod -aG "$grp" "$TARGET_USER"
        echo "NOTE : effectif seulement après une nouvelle session (ou reboot)."
    else
        echo "$TARGET_USER déjà dans le groupe $grp."
    fi
done

echo "=== [00] Préflight matériel terminé ==="

if [ "$REBOOT_REQUIRED" = "1" ]; then
    echo ""
    echo "############################################################"
    echo "# REDEMARRAGE NECESSAIRE avant de poursuivre le déploiement."
    echo "# Relance deploy.sh après le reboot : ce script est idempotent"
    echo "# et ne refera rien d'inutile."
    echo "############################################################"
    exit 42
fi
