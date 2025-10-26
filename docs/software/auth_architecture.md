# Architecture d'authentification - HouseBrain

## 🎯 Objectif et principes

### Vision générale

HouseBrain adopte une approche d'authentification **hybride** :
- **Consultation publique** : Données visibles par tous (température, historique, graphiques)
- **Actions protégées** : Modifications réservées aux utilisateurs authentifiés

### Pourquoi ce choix ?

**Cas d'usage :**
- Permettre à des visiteurs de voir l'état du système (démo, famille)
- Protéger les actions critiques (changement de température, programmation)
- Éviter les modifications accidentelles ou malveillantes

**Avantages :**
- ✅ Expérience utilisateur fluide (pas de login obligatoire pour consulter)
- ✅ Sécurité préservée (actions sensibles protégées)
- ✅ Bon pour portfolio/CV (démo publique + sécurité moderne)

---

## 🔐 Technologie : JWT (JSON Web Tokens)

### Pourquoi JWT ?

| Critère | JWT | Sessions Django classiques |
|---------|-----|---------------------------|
| **Stateless** | ✅ Pas de stockage serveur | ❌ Sessions en DB/Redis |
| **Scalabilité** | ✅ Multi-serveurs facile | ⚠️ Partage de sessions nécessaire |
| **SPA-friendly** | ✅ Parfait pour React | ⚠️ Nécessite config CORS complexe |
| **Mobile-ready** | ✅ Fonctionne partout | ❌ Cookies problématiques |
| **Standard industrie** | ✅ Utilisé partout | ⚠️ Moins moderne |

**Verdict :** JWT est le choix naturel pour une architecture SPA (React) + API (Django).

---

## 🏗️ Architecture technique

### Vue d'ensemble

```
┌─────────────────┐                    ┌─────────────────┐
│   React (SPA)   │                    │  Django + DRF   │
│                 │                    │                 │
│  - useAuth()    │◄────── HTTPS ─────►│  - JWT Auth     │
│  - localStorage │                    │  - Permissions  │
│  - Interceptor  │                    │  - ViewSets     │
└─────────────────┘                    └─────────────────┘
```

### Stack d'authentification

**Backend :**
- `djangorestframework-simplejwt` : Gestion des tokens JWT
- Permissions DRF : `IsAuthenticated`, `AllowAny`, customs
- Endpoints : `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/logout/`

**Frontend :**
- React Context API : Gestion de l'état d'authentification
- localStorage : Persistance des tokens (survit au refresh page)
- Axios interceptors : Injection automatique du token + refresh auto

---

## 🔄 Flow d'authentification complet

### 1️⃣ Login (première connexion)

```
┌─────────┐                              ┌─────────┐
│ React   │  POST /api/auth/login/       │ Django  │
│         │  { username, password }      │         │
│         │ ──────────────────────────►  │         │
│         │                              │ Vérifie │
│         │                              │ en DB   │
│         │  { access: "eyJ...",         │         │
│         │    refresh: "eyJ...",        │         │
│         │    user: {...} }             │         │
│         │ ◄──────────────────────────  │         │
│         │                              │         │
│  Stocke │                              │         │
│  tokens │                              │         │
└─────────┘                              └─────────┘
```

**Ce qui se passe côté React :**
1. Utilisateur remplit le formulaire login
2. React envoie les credentials en HTTPS
3. Django vérifie et génère 2 tokens JWT :
   - **Access token** (courte durée : 15 min) → Pour les requêtes API
   - **Refresh token** (longue durée : 7 jours) → Pour renouveler l'access
4. React stocke les tokens dans `localStorage` + state
5. L'utilisateur est maintenant authentifié

### 2️⃣ Requêtes API protégées

```
┌─────────┐                              ┌─────────┐
│ React   │  GET /api/heating/settings/  │ Django  │
│         │  Header:                     │         │
│         │  Authorization: Bearer eyJ..  │         │
│         │ ──────────────────────────►  │         │
│         │                              │ Vérifie │
│         │                              │ token   │
│         │  { data: {...} }             │ JWT     │
│         │ ◄──────────────────────────  │         │
└─────────┘                              └─────────┘
```

**Intercepteur automatique :**
```javascript
// Avant CHAQUE requête, React ajoute automatiquement :
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Django vérifie :**
1. ✅ Signature valide ? (token pas modifié)
2. ✅ Pas expiré ?
3. ✅ Utilisateur existe toujours en DB ?
4. Si tout OK → Traite la requête
5. Sinon → Renvoie `401 Unauthorized`

### 3️⃣ Refresh automatique (token expiré)

```
┌─────────┐                              ┌─────────┐
│ React   │  GET /api/heating/settings/  │ Django  │
│         │  Authorization: Bearer eyJ..  │         │
│         │ ──────────────────────────►  │         │
│         │                              │ Token   │
│         │  ❌ 401 Unauthorized          │ expiré! │
│         │ ◄──────────────────────────  │         │
│         │                              │         │
│ Détecte │                              │         │
│ 401     │  POST /api/auth/refresh/     │         │
│         │  { refresh: "eyJ..." }       │         │
│         │ ──────────────────────────►  │         │
│         │                              │ Vérifie │
│         │  { access: "eyJ_NEW..." }    │ refresh │
│         │ ◄──────────────────────────  │         │
│         │                              │         │
│ Stocke  │                              │         │
│ nouveau │  Retry GET /api/heating/     │         │
│ token   │  Authorization: Bearer NEW   │         │
│         │ ──────────────────────────►  │         │
│         │                              │         │
│         │  ✅ { data: {...} }          │         │
│         │ ◄──────────────────────────  │         │
└─────────┘                              └─────────┘
```

**Transparent pour l'utilisateur :**
- L'access token expire après 15 min
- React détecte le 401, refresh automatiquement
- Relance la requête initiale
- L'utilisateur ne voit rien (UX fluide)

### 4️⃣ Logout

```
┌─────────┐                              ┌─────────┐
│ React   │  POST /api/auth/logout/      │ Django  │
│         │  { refresh: "eyJ..." }       │         │
│         │ ──────────────────────────►  │         │
│         │                              │ Blacklist│
│         │  ✅ 204 No Content           │ (optionnel)│
│         │ ◄──────────────────────────  │         │
│         │                              │         │
│ Supprime│                              │         │
│ tokens  │                              │         │
│ locaux  │                              │         │
└─────────┘                              └─────────┘
```

**Côté React :**
1. Supprime les tokens de `localStorage`
2. Clear le state d'authentification
3. Redirige vers la page d'accueil ou login

**Côté Django (optionnel) :**
- Blacklist le refresh token pour l'invalider immédiatement
- Empêche la réutilisation du token après logout

---

## 🔑 Anatomie d'un JWT

### Structure d'un token

Un JWT ressemble à ça :
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTg0MjcyMDB9.xxxxxxxxxxx
```

Il contient **3 parties** séparées par des points :

```
[Header].[Payload].[Signature]
```

#### 1. Header (en-tête)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
→ Indique l'algorithme de cryptage utilisé

#### 2. Payload (données)
```json
{
  "user_id": 1,
  "username": "admin",
  "exp": 1698427200,  // Date d'expiration (timestamp)
  "iat": 1698426300   // Date de création
}
```
→ Contient les infos de l'utilisateur (⚠️ visible, pas crypté !)

#### 3. Signature
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  SECRET_KEY
)
```
→ Prouve que le token n'a pas été modifié

### ⚠️ Important : Le JWT n'est PAS crypté !

**On peut lire le contenu** (header + payload) :
```bash
# Décode le payload (partie 2)
echo "eyJ1c2VyX2lkIjoxLCJleHAiOjE2OTg0MjcyMDB9" | base64 -d
# {"user_id":1,"exp":1698427200}
```

**Mais on ne peut PAS le modifier** sans connaître la `SECRET_KEY` :
- Si on modifie le payload → La signature ne correspond plus
- Django rejette le token

**Moralité :**
- ✅ OK : Stocker `user_id`, `username`, `exp` dans le JWT
- ❌ JAMAIS : Stocker des mots de passe, infos bancaires, secrets

---

## 🛡️ Sécurité : Pourquoi 2 tokens ?

### Access Token (courte durée)

**Caractéristiques :**
- ⏱️ Durée : 15 minutes
- 📍 Usage : Envoyé à CHAQUE requête API
- 💾 Stockage : `localStorage` + state React
- 🎯 Risque : Si volé, validité limitée à 15 min

**Analogie :** Badge d'accès temporaire (comme dans un musée)

### Refresh Token (longue durée)

**Caractéristiques :**
- ⏱️ Durée : 7 jours
- 📍 Usage : Uniquement pour renouveler l'access token
- 💾 Stockage : `localStorage` (⚠️ idéalement HttpOnly cookie)
- 🎯 Risque : Plus sensible mais rarement utilisé

**Analogie :** Carte d'identité (pour obtenir un nouveau badge)

### Stratégie de défense

```
┌─────────────────────────────────────────────┐
│ Attaquant vole l'access token               │
│ → Valide seulement 15 min                   │
│ → Dégâts limités                            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Attaquant vole le refresh token             │
│ → Peut renouveler pendant 7 jours           │
│ → MAIS refresh rarement exposé (pas dans    │
│   headers de chaque requête)                │
│ → Détection possible (refresh depuis        │
│   nouvelle IP = alerte)                     │
└─────────────────────────────────────────────┘
```

**Bilan :**
- Si access volé → 15 min max de compromission
- Si refresh volé → Détectable + révocable via blacklist

---

## 🎨 Implémentation React : Composants clés

### 1. Context d'authentification

**Fichier :** `frontend/src/contexts/AuthContext.jsx`

**Responsabilités :**
```javascript
const AuthContext = {
  user: null,              // Infos utilisateur (username, etc.)
  isAuthenticated: false,  // true/false
  isLoading: true,         // true pendant la vérification initiale

  // Fonctions
  login(username, password),   // Authentifie l'utilisateur
  logout(),                    // Déconnexion
  refreshAccessToken(),        // Renouvelle le token
}
```

**Hook personnalisé :**
```javascript
const { user, isAuthenticated, login, logout } = useAuth();
```

### 2. Protected Routes

**Composant :** `ProtectedRoute`

**Logique :**
```javascript
if (!isAuthenticated) {
  return <Navigate to="/login" />
}
return <Outlet />  // Affiche la route protégée
```

**Usage :**
```javascript
<Route element={<ProtectedRoute />}>
  <Route path="/settings" element={<Settings />} />
  <Route path="/admin" element={<Admin />} />
</Route>
```

### 3. Affichage conditionnel

**Pattern :**
```javascript
// Page accessible à tous
function HeatingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      {/* Visible par tous */}
      <CurrentTemperature />
      <TemperatureHistory />

      {/* Visible uniquement si authentifié */}
      {isAuthenticated && (
        <button onClick={changeTemperature}>
          Modifier la température
        </button>
      )}
    </div>
  );
}
```

### 4. Intercepteur HTTP

**Axios Interceptor :**

```javascript
// Request interceptor : Ajoute le token automatiquement
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor : Gère les 401 (refresh auto)
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Tente de refresh le token
      const refreshed = await refreshAccessToken();

      if (refreshed) {
        // Retry la requête initiale avec le nouveau token
        return axios(error.config);
      }

      // Refresh échoué → Logout
      logout();
      navigate('/login');
    }
    return Promise.reject(error);
  }
);
```

---

## 🔒 Permissions Django (Backend)

### Configuration globale

**Fichier :** `backend/core/settings/base.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Par défaut = protégé
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,      # Nouveau refresh à chaque renouvellement
    'BLACKLIST_AFTER_ROTATION': True,   # Blacklist l'ancien refresh
}
```

### Permissions par ViewSet

#### Exemple 1 : Lecture publique, écriture protégée

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class HeatingViewSet(viewsets.ModelViewSet):
    queryset = Heating.objects.all()
    serializer_class = HeatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # GET → Accessible à tous
    # POST/PUT/DELETE → Authentification requise
```

#### Exemple 2 : Tout protégé sauf une action

```python
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]  # Par défaut : protégé

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def current_temperature(self, request):
        # Cette action est publique
        return Response({'temperature': 21.5})
```

#### Exemple 3 : Permission custom

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Les objets peuvent être modifiés uniquement par leur propriétaire
    """
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True

        # Écriture uniquement pour le propriétaire
        return obj.owner == request.user

class ScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    # ...
```

---

## 📊 Matrice des permissions

| Endpoint | Méthode | Permission | Utilisateur requis |
|----------|---------|------------|-------------------|
| `/api/auth/login/` | POST | AllowAny | Aucun |
| `/api/auth/refresh/` | POST | AllowAny | Aucun |
| `/api/auth/logout/` | POST | IsAuthenticated | Authentifié |
| `/api/auth/me/` | GET | IsAuthenticated | Authentifié |
| `/api/heating/` | GET | AllowAny | Aucun (lecture publique) |
| `/api/heating/` | POST/PUT/DELETE | IsAuthenticated | Authentifié |
| `/api/sensors/temperature/` | GET | AllowAny | Aucun (monitoring public) |
| `/api/scheduler/` | GET/POST/PUT/DELETE | IsAuthenticated | Authentifié |

---

## 🚨 Gestion des erreurs

### Côté Backend (Django)

```python
from rest_framework.exceptions import AuthenticationFailed

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed('Identifiants invalides')

        # Génération des tokens JWT
        # ...
```

**Codes HTTP :**
- `401 Unauthorized` → Token invalide/expiré
- `403 Forbidden` → Token valide mais pas les permissions
- `400 Bad Request` → Credentials invalides

### Côté Frontend (React)

```javascript
async function login(username, password) {
  try {
    const response = await axios.post('/api/auth/login/', {
      username,
      password
    });

    // Succès : stocke les tokens
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);

  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Identifiants incorrects');
    }
    throw new Error('Erreur de connexion au serveur');
  }
}
```

**Affichage utilisateur :**
```javascript
{error && <div className="error">{error}</div>}
```

---

## 🧪 Tests de validation

### Tests Backend (Django)

```python
from rest_framework.test import APITestCase

class AuthenticationTests(APITestCase):
    def test_login_success(self):
        """Test login avec credentials valides"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_protected_endpoint_without_token(self):
        """Test accès endpoint protégé sans token"""
        response = self.client.post('/api/heating/', {...})
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_with_token(self):
        """Test accès endpoint protégé avec token valide"""
        token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.post('/api/heating/', {...})
        self.assertEqual(response.status_code, 201)
```

### Tests Frontend (React)

**Tests manuels :**
1. ✅ Login avec bon credentials → Tokens stockés
2. ✅ Login avec mauvais credentials → Message d'erreur
3. ✅ Accès page protégée sans login → Redirection `/login`
4. ✅ Accès page protégée avec login → Page affichée
5. ✅ Bouton protégé visible uniquement si authentifié
6. ✅ Logout → Tokens supprimés + redirection
7. ✅ Refresh page après login → Reste authentifié
8. ✅ Token expiré → Refresh automatique transparent

---

## 📈 Évolutions futures possibles

### Court terme
- ✅ Rate limiting sur `/api/auth/login/` (éviter brute force)
- ✅ Logs des tentatives de connexion échouées
- ✅ Email d'alerte en cas de connexion depuis nouvelle IP

### Moyen terme
- 🔄 Authentification à 2 facteurs (2FA)
- 🔄 Social login (Google, GitHub)
- 🔄 Sessions multiples (voir les appareils connectés)

### Long terme
- 🚀 OAuth2 / OpenID Connect (si API publique)
- 🚀 Rôles multiples (admin, user, guest)
- 🚀 Permissions granulaires par ressource

---

## 📚 Ressources

- [Django REST Framework - Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [djangorestframework-simplejwt Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT.io - Introduction aux JWT](https://jwt.io/introduction)
- [OWASP - Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Date de création :** Octobre 2025
**Auteur :** Emmanuel Oudot
**Projet :** HouseBrain - Système de gestion domotique

---

