# AI Heating Modification - Backend

Endpoint Django et architecture LLM pour la modification des plannings de chauffage en langage naturel.

---

## Vue d'ensemble

L'app Django `ai` expose un endpoint POST qui reçoit une instruction utilisateur et le plan courant, interroge un LLM, valide le résultat et retourne le plan modifié.

---

## Architecture

### Structure des fichiers

```
backend/ai/
├── api/
│   ├── serializers.py         # Validation de l'input
│   ├── urls.py                # Routage
│   └── views.py               # Point d'entrée HTTP
└── services/
    ├── llm_client.py          # Interface abstraite LLM
    ├── groq_client.py         # Implémentation Groq
    ├── plan_modifier.py       # Orchestration : prompt → LLM → validation
    ├── prompt_builder.py      # Assembleur générique de prompts
    └── prompts/
        ├── heating.py         # Format JSON + assemblage du prompt heating
        └── heating_rules.py   # Règles métier injectées dans le prompt
```

---

## API REST

### Modifier un planning via IA

```
POST /api/ai/heating/modify/
```

**Authentification requise** (JWT Bearer token)

**Body :**
```json
{
  "instruction": "Allume le chauffage de la chambre R de 10h à 12h à 21 degrés",
  "plan": {
    "date": "2025-12-27",
    "rooms": [
      {
        "room_id": 1,
        "name": "Salon",
        "slots": [
          {"start": "07:00", "end": "09:00", "type": "temp", "value": 19.5}
        ]
      }
    ]
  }
}
```

**Réponse succès (200) :**
```json
{
  "date": "2025-12-27",
  "rooms": [...]
}
```

**Réponse erreur (400) :**
```json
{
  "detail": "Message d'erreur explicite en français"
}
```

---

## Services

### llm_client.py — Interface abstraite

Classe abstraite `LLMClient` avec une seule méthode à implémenter :

```python
def generate(self, system_prompt: str, user_prompt: str) -> str
```

Permet de changer de provider LLM sans modifier la logique métier.

### groq_client.py — Implémentation Groq

**Modèle :** `llama-3.3-70b-versatile`

**Configuration :**
- `temperature: 0.2` — quasi-déterministe pour du JSON structuré
- `max_tokens: 4096` — suffisant pour un plan complet avec 10 pièces

**Gestion des erreurs :**
- `RateLimitError` → message avec délai de retry parsé depuis la réponse Groq
- `APIError` → message générique d'indisponibilité
- Toutes les erreurs sont converties en `DRFValidationError` (400) avec message lisible

**Exemple de message rate limit :**
`"Le service IA a atteint sa limite quotidienne. Réessayez dans 58 minutes."`

### plan_modifier.py — Orchestration

Fonction principale :
```python
def modify_heating_plan(instruction: str, plan: dict) -> dict
```

**Étapes :**
1. Construction du prompt via `prompt_builder` + `prompts/heating.py`
2. Appel LLM via `_get_llm_client()`
3. Parsing JSON de la réponse (avec strip markdown défensif)
4. Vérification du champ `success` retourné par le LLM
5. Validation métier via `HeatingPattern.get_or_create_from_slots()`
6. Retour du plan nettoyé (sans champs `success`/`reason`)

**Pour changer de provider LLM :**
Modifier uniquement `_get_llm_client()` dans `plan_modifier.py`.

### prompts/heating_rules.py — Règles métier

Fichier dédié aux règles injectées dans le system prompt. À modifier en priorité pour améliorer la qualité des réponses LLM sans toucher à l'architecture.

**Règles couvertes :**
- Format des slots (HH:MM, durée minimum 30 min)
- Type unique par pièce (temp ou onoff)
- Valeurs valides (temp: 0-30, onoff: "on"/"off")
- Résolution des chevauchements (4 cas avec exemples concrets)
- Références temporelles ambiguës ("soir" → 18:00-22:00, etc.)
- Reporting succès/échec via champs `success` et `reason`

---

## Champ success/reason

Le LLM retourne toujours un champ `success` et `reason` :

```json
{
  "success": false,
  "reason": "Aucune pièce nommée 'chambre des invités' dans le plan.",
  "date": "...",
  "rooms": [...]
}
```

Si `success: false` → le backend lève une `DRFValidationError` avec le `reason` → affiché à l'utilisateur.
Si `success: true` → les champs `success` et `reason` sont retirés avant retour au frontend.

---

## Validation du plan retourné

Réutilise la logique existante de `HeatingPattern.get_or_create_from_slots()` qui déclenche `HeatingPattern.clean()` :
- Pas de chevauchement de slots
- Durée minimum 30 minutes
- Type unique par pièce
- Valeurs cohérentes avec le type

Si la validation échoue → `DRFValidationError` avec le détail de l'erreur par pièce.

---

## Configuration

**Variables d'environnement :**
```
GROQ_API_KEY=your_key_here
```

**Settings Django :**
```python
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

**INSTALLED_APPS :**
```python
"ai",
```

**urls.py (core) :**
```python
path("ai/", include("ai.api.urls")),
```

---

## Logs

```bash
# Requêtes IA et réponses LLM
sudo journalctl -u housebrain -f | grep "AI heating"

# Erreurs Groq
sudo journalctl -u housebrain -f | grep "Groq"
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Avril 2026
