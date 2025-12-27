# Authentification JWT

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

## Backend

### Configuration

**Settings (base.py) :**
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

### Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/login/` | POST | Connexion (retourne access token + cookie refresh) |
| `/api/auth/refresh/` | POST | Renouvellement access token (lit refresh depuis cookie) |
| `/api/auth/me/` | GET | Informations utilisateur connecté |
| `/api/auth/logout/` | POST | Déconnexion (supprime cookie refresh) |

### Views personnalisées

**CookieTokenObtainPairView :**
- Hérite de `TokenObtainPairView`
- Place le refresh token dans un cookie HttpOnly
- Retourne uniquement l'access token en JSON

**CookieTokenRefreshView :**
- Hérite de `TokenRefreshView`
- Lit le refresh token depuis le cookie
- Retourne un nouvel access token

---

## Frontend

### Context API

**AuthProvider :**
```javascript
{
  user,           // Objet utilisateur { username }
  accessToken,    // Access token JWT
  login,          // Fonction de connexion
  logout,         // Fonction de déconnexion
  refresh,        // Fonction de refresh manuel
  loading,        // État de chargement initial
}
```

### Services

**login(username, password) :**
- POST `/api/auth/login/`
- Retourne `{ access }`

**refresh() :**
- POST `/api/auth/refresh/`
- Lit refresh token depuis cookie
- Retourne `{ access }`

**getUser(token) :**
- GET `/api/auth/me/`
- Header `Authorization: Bearer {token}`
- Retourne `{ username }`

**logout() :**
- POST `/api/auth/logout/`
- Supprime cookie refresh token

### fetchWithAuth

Wrapper fetch avec retry automatique :
```javascript
fetchWithAuth(url, options, refreshCallback)
```

Comportement :
1. Effectue la requête
2. Si 401, appelle `refreshCallback()` pour obtenir nouveau token
3. Retry la requête avec le nouveau token
4. Si échec refresh, throw error

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

## Gestion des erreurs

### Backend
- Token invalide : 401 Unauthorized
- Refresh token manquant : 401 Unauthorized
- Refresh token expiré : 401 Unauthorized

### Frontend
- Refresh échoué : déconnexion automatique
- 401 non récupérable : message "Session expired"

---

## Sécurité

### Cookies
- `httponly=True` : pas accessible via JavaScript
- `secure=True` : transmission HTTPS uniquement
- `samesite='Strict'` : protection CSRF

### Tokens
- Access token courte durée (15 min)
- Refresh token longue durée (7 jours)
- Header Authorization standard

### HTTPS
Configuration obligatoire en production :
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 2025
