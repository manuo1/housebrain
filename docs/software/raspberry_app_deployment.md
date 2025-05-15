⚠️Avant de commencer le déploiement il est important de paramétrer une IP fixe pour votre Raspberry 

=> Voir dans les paramètres de votre Box Internet

---

Dans un terminal, connectez vous au raspberry :

```bash
ssh admin@housebrain
```
Sur votre Raspberry Pi :

```bash
cd /home/admin
git clone https://github.com/manuo1/housebrain.git
cd housebrain/backend

# Rendre le script de déploiement exécutable
chmod +x deployment/scripts/deploy.sh

# Exécuter le script de déploiement
./deployment/scripts/deploy.sh
```