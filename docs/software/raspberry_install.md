
# Installation et Préparation de la Clé USB pour Raspberry Pi

## Matériel requis :

- Raspberry Pi 3 B+
- Clé USB
- Alimentation micro-USB 5V 2.5A

---

## Préparation de la clé USB :

### 1. Télécharger Raspberry Pi Imager

- Lien officiel : [Télécharger Raspberry Pi Imager](https://www.raspberrypi.com/software/)

### 2. Lancer Raspberry Pi Imager

- **Choisir le modèle de Raspberry Pi** : Raspberry Pi 3
- **Choisir le système d'exploitation** : Raspberry Pi OS **Lite** (64-bit)
- **Stockage** : Sélectionner la clé USB

### 3. Configuration de l'OS :

Lors de la question **"Voulez-vous appliquer les réglages de personnalisation de l'OS ?"**, répondre **"MODIFIER RÉGLAGES"**. Puis, configurer les éléments suivants :

#### **Général :**
- **Nom d'hôte** : `housebrain`
- **Nom d'utilisateur** : `admin`
- **Mot de passe** : [Votre mot de passe]
- **Configurer le Wi-Fi** : Saisir les informations de votre réseau Wi-Fi  
  ⚠️ **Pays Wi-Fi** : FR
- **Réglages locaux :**
  - **Fuseau horaire** : Europe/Paris
  - **Type de clavier** : Français (fr)


#### **Services :**
- **Activer SSH** : Utiliser un mot de passe pour l’authentification

De retour sur **"Voulez-vous appliquer les réglages de personnalisation de l'OS ?"**, répondre **"OUI"**. 

---

### 4. Flashage de l'image :

Attendre que l'image soit flashée sur la clé USB

---

## Premier démarrage :

1. Insérez la clé USB, branchez l'alimentation.
2. Attendez environ 1 à 2 minutes pour le démarrage.

### Connexion SSH :

Dans un terminal, tapez la commande suivante :
```bash
ssh admin@housebrain.local
```

- Lorsque vous y êtes invité, tapez **`yes`** pour accepter la connexion.
- Utilisez le mot de passe défini lors de la création de la clé USB.

---

## Mise à jour et installation de Git :

Pour mettre à jour le système et installer Git, exécutez les commandes suivantes :

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git -y
```
