#!/bin/bash
# Suppression complète du dossier HouseBrain

echo "Suppression complète du dossier /home/admin/housebrain..."

# Supprimer les protections d'écriture (si nécessaire)
sudo chmod -R u+w /home/admin/housebrain

# Suppression forcée et silencieuse
sudo rm -rf /home/admin/housebrain

echo "Le dossier /home/admin/housebrain a été supprimé avec succès."


