## Ip Fixe

⚠️Avant de commencer le déploiement il est nécessaire de paramétrer une IP fixe pour votre Raspberry 

=> Voir dans les paramètres de votre Box Internet


## Activer le Port Série (Indispensable pour la lecture de la Téléformation)

```bash
sudo raspi-config
```
Choisir : 
    - 3 Interface Options    Configure connections to peripherals
    - I6 Serial Port Enable/disable shell messages on the serial connection
    - Would you like a login shell to be accessible over serial?   => ⚠️ Répondre No ⚠️
    - Would you like the serial port hardware to be enabled? => ⚠️ Répondre Yes ⚠️

la config sera :

```bash
The serial login shell is disabled
The serial interface is enabled  
```

Redémarrer le Raspberry

```bash
sudo reboot 
```

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