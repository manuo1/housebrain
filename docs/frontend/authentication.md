# Authentification JWT - Frontend

Gestion de l'authentification avec JWT côté client React.

---

## Vue d'ensemble

### Architecture
- **AuthContext** global via Context API
- **Services** dédiés pour les appels API d'authentification
- **fetchWithAuth** : wrapper fetch avec refresh automatique
- Pas de stockage localStorage (refresh token en cookie HttpOnly)

### Structure des fichiers

```
src/
├── contexts/
│   ├── AuthContext.js       # Context React
│   ├── AuthProvider.jsx     # Provider avec logique métier
│   └── useAuth.js           # Hook personnalisé
└── services/
    ├── auth/
    │   ├── login.js         # POST /api/auth/login/
    │   ├── logout.js        # POST /api/auth/logout/
    │   ├── refresh.js       # POST /api/auth/refresh/
    │   └── getUser.js       # GET /api/auth/me/
    ├── fetchWithAuth.js     # Wrapper fetch avec retry 401
    └── fetchJson.js         # Wrapper fetch basique
```

---

## AuthContext

### État fourni

**Fichier :** `src/contexts/AuthContext.js`

```javascript
{
  user,           // { username } ou null
  accessToken,    // string ou null
  login,          // async (username, password) => void
  logout,         // async () => void
  refresh,        // async () => string (nouveau token)
  loading,        // boolean - chargement initial
}
```

### Hook useAuth

**Fichier :** `src/contexts/useAuth.js`

```javascript
import { useAuth } from '../contexts/useAuth';

const { user, accessToken, login, logout, refresh } = useAuth();
```

---

## AuthProvider

**Fichier :** `src/contexts/AuthProvider.jsx`

### Initialisation au montage

Au chargement de l'app :
1. Tente de récupérer l'utilisateur avec token existant
2. Si échec (token expiré), tente un refresh automatique
3. Si le refresh échoue, utilisateur reste déconnecté
4. Permet de maintenir la session après refresh de page

### Fonctions exposées

**login(username, password) :**
- Appelle `loginApi()`
- Stocke l'access token en state
- Récupère les données utilisateur
- Met à jour le state `user`

**logout() :**
- Appelle `logoutApi()` (supprime cookie refresh)
- Clear state `user` et `accessToken`

**refresh() :**
- Appelle `refreshApi()`
- Met à jour `accessToken`
- Retourne le nouveau token
- En cas d'échec : clear state et throw error

---

## Services d'authentification

### login(username, password)

**Fichier :** `src/services/auth/login.js`

**Appel :**
```javascript
POST /api/auth/login/
Body: { username, password }
```

**Retour :**
```javascript
{ access: "eyJ0eXAiOiJKV1QiLCJhbGc..." }
```

### refresh()

**Fichier :** `src/services/auth/refresh.js`

**Appel :**
```javascript
POST /api/auth/refresh/
// Cookie refresh_token envoyé auto avec credentials: 'include'
```

**Retour :**
```javascript
{ access: "eyJ0eXAiOiJKV1QiLCJhbGc..." }
```

### getUser(token)

**Fichier :** `src/services/auth/getUser.js`

**Appel :**
```javascript
GET /api/auth/me/
Headers: { Authorization: "Bearer {token}" }
```

**Retour :**
```javascript
{ username: "admin" }
```

### logout()

**Fichier :** `src/services/auth/logout.js`

**Appel :**
```javascript
POST /api/auth/logout/
```

**Side-effect :**
- Cookie `refresh_token` supprimé par le backend

---

## fetchWithAuth

**Fichier :** `src/services/fetchWithAuth.js`

### Principe

Wrapper autour de `fetch` qui gère automatiquement le refresh du token en cas d'expiration (401).

### Signature

```javascript
fetchWithAuth(url, options, refreshCallback)
```

### Comportement

```
1. Effectue la requête avec le token actuel
2. Si 401 ET refreshCallback fourni :
   a. Appelle refreshCallback() pour obtenir nouveau token
   b. Retry la requête avec le nouveau token
3. Si refresh échoue : throw error "Session expired"
4. Retourne la réponse
```

### Exemple d'utilisation

```javascript
import fetchWithAuth from '../services/fetchWithAuth';
import { useAuth } from '../contexts/useAuth';

const { accessToken, refresh } = useAuth();

const response = await fetchWithAuth(
  '/api/rooms/',
  {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  },
  refresh
);

const data = await response.json();
```

---

## Gestion des erreurs

### Erreurs de connexion

**Cas :**
- Credentials incorrects
- Backend non disponible

**Comportement :**
- Throw error avec message
- Pas de stockage d'état

### Erreurs de refresh

**Cas :**
- Refresh token expiré (après 7 jours)
- Cookie manquant

**Comportement :**
- Déconnexion automatique
- Throw error "Session expired"

---

## Stockage et sécurité

### Access token

**Méthode :** State React (via Context API)

**Caractéristiques :**
- Perdu au refresh de page
- Récupéré automatiquement via refresh token

### Refresh token

**Méthode :** Cookie HttpOnly défini par le backend

**Caractéristiques :**
- Pas accessible via JavaScript (protection XSS)
- Envoyé automatiquement à chaque requête
- Durée de vie : 7 jours
- `credentials: 'include'` requis dans les appels fetch

---

## Flux utilisateur

### Première connexion
```
1. Utilisateur entre username/password
2. Frontend appelle login()
3. Backend retourne access token + set cookie refresh
4. Frontend stocke access token en state
5. Frontend récupère user info
6. Utilisateur connecté
```

### Navigation dans l'app
```
1. Composant appelle API avec access token
2. Si token valide → données retournées
3. Si 401 → refresh automatique puis retry
4. Si refresh KO → déconnexion
```

### Refresh de page
```
1. State perdu (access token effacé)
2. Cookie refresh token toujours présent
3. useEffect init() détecte absence de user
4. Appelle refresh() automatiquement
5. Nouveau access token obtenu
6. Navigation continue normalement
```

### Déconnexion
```
1. Utilisateur clique "Logout"
2. Frontend appelle logout()
3. Backend supprime cookie refresh
4. Frontend clear state (user, accessToken)
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Décembre 20
