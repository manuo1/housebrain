# Notifications

Module générique d'envoi de notifications, découplé des apps métier qui les déclenchent.

---

## Vue d'ensemble

L'app `notifications` centralise le journal et l'envoi de toute notification émise par HouseBrain, quel que soit l'événement d'origine (ouverture de porte, conso excessive, perte de données Linky, etc.). Les apps métier n'ont aucune connaissance du mécanisme d'envoi : elles appellent simplement `NotificationService.notify()`.

`event_code` est une chaîne libre (pas un choix figé) : n'importe quelle app peut introduire un nouveau type d'événement sans modifier `notifications`.

**Canal actuel :** email (SMTP) uniquement. Un seul destinataire (Emmanuel), configuré en `.env`. SMS et push écartés (pas d'abonnement Free Mobile compatible, refus de dépendre d'une application tierce).

---

## Modèle Notification

```python
event_code               # Identifiant libre de l'événement (ex: garage_door_opened)
level                     # INFO / WARNING / CRITICAL
message                   # Corps du message
triggered_by_username     # Username libre de l'utilisateur à l'origine de l'action, si applicable (pas de FK — évite le couplage avec authentication)
status                    # PENDING / SENT / FAILED
created_at                # Horodatage de création
sent_at                   # Horodatage d'envoi réussi (null si jamais envoyé)
```

Chaque tentative de notification est journalisée, y compris en cas d'échec d'envoi — la ligne survit toujours, seul le `status` change.

---

## Services

### EmailBackend

`EmailBackend.send(subject, message)` — wrapper fin autour de `django.core.mail.send_mail`, utilise les settings dédiés `NOTIFICATIONS_EMAIL_*`. Lève `EmailBackendError` si le destinataire n'est pas configuré ou si l'envoi SMTP échoue.

### NotificationService

`NotificationService.notify(event_code, message, level=INFO, triggered_by_username="")` — point d'entrée générique appelé par n'importe quelle app :

1. Crée la ligne `Notification` (statut `PENDING`).
2. Tente l'envoi via `EmailBackend.send()`.
3. Met à jour `status` (`SENT`/`FAILED`) et `sent_at`.

Exécution synchrone (pas de queue/Celery) — cohérent avec le reste du projet, volume de notifications trop faible pour justifier l'asynchrone actuellement.

---

## Configuration SMTP (.env)

```
NOTIFICATIONS_EMAIL_HOST=smtp.gmail.com
NOTIFICATIONS_EMAIL_PORT=587
NOTIFICATIONS_EMAIL_USER=compte@gmail.com
NOTIFICATIONS_EMAIL_PASSWORD=mot_de_passe_application
NOTIFICATIONS_EMAIL_RECIPIENT=destinataire@exemple.fr
```

**Gmail + mot de passe d'application :** l'auth SMTP avec le mot de passe Gmail habituel est bloquée par Google. Un mot de passe d'application dédié (16 caractères, généré via `myaccount.google.com/apppasswords`, nécessite la validation en 2 étapes) est requis à la place — révocable indépendamment du reste du compte.

---

## Administration Django

**NotificationAdmin** : consultation seule (ajout/modification/suppression désactivés) — sert de journal d'audit, pas d'interface de gestion.

---

## Prochaine étape (V2, pas commencée)

Actions déclenchables par réponse à une notification email, limitées à des actions sûres (ex : fermer une porte déjà ouverte — jamais l'ouvrir).

Approche retenue : lien signé avec expiration embarqué dans le mail (`django.core.signing`), cliquable directement — pas de parsing de réponse en texte libre, pas de boîte mail entrante (IMAP) à gérer. Whitelist stricte des actions autorisées par `event_code`.

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
