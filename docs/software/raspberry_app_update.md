Dans un terminal, connectez vous au raspberry :

```bash
ssh admin@housebrain
```
Sur votre Raspberry Pi :

Pour la partie Backend uniquement :

```bash
# Rendre le script de mise à jour exécutable
chmod +x /home/admin/housebrain/backend/deployment/scripts/update.sh

# Exécuter le script de mise à jour
/home/admin/housebrain/backend/deployment/scripts/update.sh
```

Pour la partie Backend et Frontend :

```bash
# Rendre le script de mise à jour exécutable
chmod +x /home/admin/housebrain/backend/deployment/scripts/update_frontend.sh

# Exécuter le script de mise à jour
/home/admin/housebrain/backend/deployment/scripts/update_frontend.sh
```