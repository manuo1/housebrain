#!/bin/bash
# Réinitialisation des permissions et suppression des configurations

# Retirer www-data du groupe admin
sudo gpasswd -d www-data admin 2>/dev/null || echo "www-data n'était pas dans le groupe admin"

# Réinitialiser les permissions du home
sudo chmod 755 /home/admin

# Réinitialiser les permissions de housebrain
if [ -d "/home/admin/housebrain" ]; then
    sudo chown -R admin:admin /home/admin/housebrain
    echo "Permissions de /home/admin/housebrain réinitialisées."
fi

echo "Permissions réinitialisées avec succès."
