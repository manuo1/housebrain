#!/bin/bash
# Création du superutilisateur Django (une seule fois)
# Idempotent : vérifie d'abord si un superuser existe déjà avant de proposer la
# création interactive. Rejouable sans risque à chaque déploiement/update.

cd /home/admin/housebrain/backend
source .venv/bin/activate

SUPERUSER_EXISTS=$(python manage.py shell -c "
from django.contrib.auth import get_user_model
print(get_user_model().objects.filter(is_superuser=True).exists())
" | tail -n 1)

if [ "$SUPERUSER_EXISTS" = "True" ]; then
    echo "Un superutilisateur existe déjà, création ignorée."
else
    echo "Aucun superutilisateur trouvé."
    echo "Veuillez entrer les informations pour le superutilisateur :"
    python manage.py createsuperuser
    echo "Superutilisateur Django créé avec succès."
fi

deactivate
