# Authentification JWT - Backend

Système d'authentification avec JWT et cookies HttpOnly pour HouseBrain.

---

## Vue d'ensemble

### Architecture
- JWT avec `djangorestframework-simplejwt`
- Access token (15 min) : transmis en JSON
- Refresh token (7 jours) : stocké dans cookie HttpOnly
- Refresh automatique côté frontend sur expiration

### Stratégie de sécurité
- Routes publiques : lecture seule (GET)
- Routes protégées : écriture uniquement (POST/PUT/DELETE)

---

## Configuration Django

### Settings (base.py)

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

---

## Endpoints API

### Routes d'authentification

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/login/` | POST | Connexion (retourne access token + cookie refresh) |
| `/api/auth/refresh/` | POST | Renouvellement access token (lit refresh depuis cookie) |
| `/api/auth/me/` | GET | Informations utilisateur connecté |
| `/api/auth/logout/` | POST | Déconnexion (supprime cookie refresh) |

---

## Views personnalisées

### CookieTokenObtainPairView

**Hérite de :** `TokenObtainPairView`

**Fonctionnement :**
- Reçoit `username` et `password` en POST
- Place le refresh token dans un cookie HttpOnly
- Retourne uniquement l'access token en JSON

**Réponse :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Cookie défini :**
```
Set-Cookie: refresh_token=eyJ0eXAiOiJKV1QiLCJhbGc...;
            HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

### CookieTokenRefreshView

**Hérite de :** `TokenRefreshView`

**Fonctionnement :**
- Lit le refresh token depuis le cookie `refresh_token`
- Valide le refresh token
- Retourne un nouvel access token

**Réponse :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Gestion des erreurs

### Codes d'erreur HTTP

**401 Unauthorized :**
- Token invalide
- Refresh token manquant
- Refresh token expiré
- Credentials incorrects

**403 Forbidden :**
- Permissions insuffisantes pour l'action demandée

---

## Sécurité

### Configuration des cookies

```python
# Production settings
httponly=True     # Pas accessible via JavaScript
secure=True       # Transmission HTTPS uniquement
samesite='Strict' # Protection CSRF
max_age=604800    # 7 jours
```

### Headers de sécurité

**Authorization standard :**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### HTTPS obligatoire en production

```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## Durée de vie des tokens

| Token | Durée | Usage |
|-------|-------|-------|
| Access token | 15 minutes | Authentification des requêtes API |
| Refresh token | 7 jours | Renouvellement de l'access token |

**Stratégie :**
- Access token courte durée → sécurité renforcée
- Refresh token longue durée → meilleure UX (pas de reconnexion fréquente)

---

## Flux d'authentification

### Connexion
```
1. User entre credentials
2. POST /api/auth/login/
3. Backend retourne { access }
4. Backend set cookie refresh_token (HttpOnly)
5. Frontend stocke access dans state
6. Frontend GET /api/auth/me/ avec access token
7. Frontend stocke user dans state
```

### Requête protégée
```
1. Frontend envoie requête avec header Authorization: Bearer {access}
2. Si 401 (token expiré):
   a. POST /api/auth/refresh/ (cookie refresh envoyé auto)
   b. Backend retourne { access }
   c. Retry requête avec nouveau access token
3. Si refresh échoue: déconnexion
```

### Déconnexion
```
1. POST /api/auth/logout/
2. Backend delete cookie refresh_token
3. Frontend clear user et accessToken
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
