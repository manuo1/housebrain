Dans un terminal, connectez vous au raspberry :

```bash
ssh admin@housebrain
```
Sur votre Raspberry Pi :

```bash
# Rendre le script de désinstallation exécutable
chmod +x /home/admin/housebrain/backend/deployment/scripts/remove.sh

# Exécuter le script de désinstallation
/home/admin/housebrain/backend/deployment/scripts/remove.sh
```