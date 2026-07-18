
# Installation et Préparation du support de démarrage pour Raspberry Pi

## Matériel requis :

- Raspberry Pi 3 B+
- Support de démarrage : clé USB ou SSD (via adaptateur USB)
- Alimentation micro-USB 5V 2.5A

---

## Préparation du support de démarrage :

### 1. Télécharger Raspberry Pi Imager

- Lien officiel : [Télécharger Raspberry Pi Imager](https://www.raspberrypi.com/software/)

### 2. Lancer Raspberry Pi Imager

- **Choisir le modèle de Raspberry Pi** : Raspberry Pi 3
- **Choisir le système d'exploitation** : Raspberry Pi OS **Lite** (64-bit)
- **Stockage** : Sélectionner la clé USB ou le SSD

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

Attendre que l'image soit flashée sur le support (clé USB ou SSD).

Sur SSD via adaptateur USB, un port USB peut parfois ne pas suffire à démarrer
correctement (échec de boot) - tester un autre port USB du Pi si le premier
démarrage échoue.

---

## Premier démarrage :

1. Insérez le support (clé USB ou SSD), branchez l'alimentation.
2. Attendez environ 1 à 2 minutes pour le démarrage.

### Connexion SSH :

Dans un terminal, tapez la commande suivante :
```bash
ssh admin@housebrain
```

- Lorsque vous y êtes invité, tapez **`yes`** pour accepter la connexion.
- Utilisez le mot de passe défini lors du flashage.

Si vous réutilisez un hostname/IP déjà connu de SSH (réinstallation sur le même
Pi), purgez l'ancienne clé d'hôte si besoin :
```bash
ssh-keygen -R housebrain
```

---

## Mise à jour et installation de Git :

Git n'est pas installé par défaut sur l'image Lite, et doit l'être manuellement
avant de pouvoir cloner le repo (le script de déploiement se charge ensuite
lui-même de la mise à jour système et des autres dépendances) :

```bash
sudo apt update
sudo apt install -y git
```

Voir la suite dans `raspberry_app_deployment.md` (clonage du repo puis
déploiement).
