#!/bin/bash
# Suppression complète du dossier HouseBrain

# Vérification avant suppression
read -p "Voulez-vous vraiment supprimer le dossier /home/admin/housebrain et tout son contenu ? (o/N) : " confirm
if [[ "$confirm" =~ ^[oO]$ ]]; then
    sudo rm -rf /home/admin/housebrain
    echo "Le dossier /home/admin/housebrain a été supprimé avec succès."
else
    echo "Suppression annulée."
fi
