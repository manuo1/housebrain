# AI Heating Duplication - Backend

Endpoint Django conversationnel pour dupliquer un planning de chauffage vers d'autres jours en langage naturel.

---

## Vue d'ensemble

Remplace l'ancien mécanisme de duplication day/week (formulaire avec datepickers, sélecteur de jours) par un chat en langage naturel. Protocole conversationnel multi-tours : le LLM extrait uniquement les champs (`room_ids`/`weekdays`/`start`/`end`) depuis l'instruction, tout le reste (validation métier, calcul des occurrences, message de récapitulatif, exécution) est déterministe côté Python.

---

## Architecture

### Structure des fichiers

```
backend/ai/
├── api/
│   ├── serializers.py                     # AiHeatingPlanDuplicateInputSerializer
│   ├── urls.py
│   └── views.py                           # AiHeatingPlanDuplicateView
└── services/
    ├── duplication_interpreter.py         # Appel LLM + validation de forme
    └── prompts/
        ├── duplication.py                 # Format JSON + assemblage du prompt
        └── duplication_rules.py           # Règles métier d'extraction injectées dans le prompt

backend/heating/api/
├── selectors.py                           # get_room_names_by_ids, get_room_heating_day_plan_data
└── services.py                            # validate_ai_duplication_request, build_ai_duplication_recap,
                                            # generate_duplication_dates
```

---

## Protocole conversationnel

### Champs échangés

- `echanges` : liste `[{role: "user"|"assistant", content: str}, ...]`, s'enrichit à chaque aller-retour, contexte complet envoyé à chaque requête
- `step` : `"clarify"` en entrée (défaut, tous les cas sauf validation finale) ou `"validate"` (déclenche l'exécution) — en sortie, calculé par le back : `"clarify"`, `"to_validate"`, `"error"`
- `source_date` : fixe, connue seulement du front, jamais transmise au LLM (sert uniquement en Python : liste de pièces proposées, ligne d'intro du recap)
- `data` : `{room_ids, weekdays, start, end}` — affichage/traçabilité côté front uniquement, **jamais fait confiance en entrée** ; le back revalide systématiquement via `validate_ai_duplication_request` avant d'exécuter au step `validate`

### Endpoint

```
POST /api/ai/heating/duplicate/
```

**Authentification requise** (JWT Bearer token)

**Body (step clarify) :**
```json
{
  "source_date": "2026-08-18",
  "echanges": [
    {"role": "user", "content": "copie le planning de la chambre tous les mercredis jusqu'à fin septembre"}
  ],
  "step": "clarify"
}
```

**Réponse (to_validate) :**
```json
{
  "echanges": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "Je récapitule, vous voulez copier le planning de Chambre du mardi 18 août 2026 sur tous les mercredi entre le mercredi 19 août 2026 et le mercredi 30 septembre 2026 ?"}
  ],
  "step": "to_validate",
  "source_date": "2026-08-18",
  "data": {"room_ids": [2], "weekdays": [2], "start": "2026-08-19", "end": "2026-09-30"}
}
```

**Body (step validate, après confirmation "oui") :**
```json
{
  "source_date": "2026-08-18",
  "echanges": [...],
  "step": "validate",
  "data": {"room_ids": [2], "weekdays": [2], "start": "2026-08-19", "end": "2026-09-30"}
}
```

**Réponse (succès) :**
```json
{"status": "validated", "created_updated": 7}
```

**Réponse (erreur métier au validate, ex: data trafiquée)** : revient en `step: "clarify"` avec un message assistant explicatif ajouté aux `echanges`, jamais un step `"error"` terminal — récupérable, l'utilisateur peut préciser.

---

## Vue — `AiHeatingPlanDuplicateView`

**Fichier :** `ai/api/views.py`

### Garde-fou

`MAX_EXCHANGES_BEFORE_GIVING_UP = 10` (~5 aller-retours). Au-delà, `step: "error"` terminal avec message générique "recommencez depuis le début" — seul cas de step `"error"`. Toute autre erreur (validation métier incohérente, aucune occurrence dans la période) reste en `"clarify"`, jamais bloquante.

### Flux step `clarify`

1. Re-interprète toute la conversation via `interpret_duplication_instruction` à chaque appel (pas de mémoire d'état côté back entre deux requêtes, tout repart de `echanges`)
2. Si LLM renvoie `status != "ready"` → message assistant ajouté, `step: "clarify"`
3. Si `ready` → `validate_ai_duplication_request` (heating/api/services.py) : si erreur → message assistant, `step: "clarify"` ; si ok/warning → `build_ai_duplication_recap` génère la phrase de confirmation (100% déterministe, pas de LLM), `step: "to_validate"`

### Flux step `validate`

Revalide intégralement `data` reçu (jamais fait confiance) via `validate_ai_duplication_request`, puis exécute via `duplicate_heating_plan_with_override` pour chaque pièce.

---

## Services — `heating/api/services.py`

### `generate_duplication_dates(start_date, weekdays, end_date) -> list[date]`

Calcule les occurrences effectives (dates concrètes) à partir de `start`/`weekdays`/`end`. Réutilisé pour la validation (compte des jours impactés) et l'exécution.

### `validate_ai_duplication_request(room_ids, weekdays, start, end, known_room_ids, today) -> dict`

Retourne `{"status": "ok"|"warning"|"error", "message": str, "nb_days_impacted": int}`.

**Règles :**
- `room_ids` non vide, sans doublon, tous connus (`known_room_ids` = pièces ayant un planning à `source_date`)
- `weekdays` non vide, sans doublon, valeurs 0-6
- `start`/`end` parsables, `start >= today` (aujourd'hui non terminé, son plan reste modifiable), `end >= start`
- Période ≤ `AI_DUPLICATION_MAX_DAYS` (365 jours)
- Au moins une occurrence effective dans la période sinon erreur
- Si occurrences > `AI_DUPLICATION_WARNING_THRESHOLD` (30) → `status: "warning"` (non bloquant, juste confirmation renforcée), message ajouté après le recap

### `build_ai_duplication_recap(...) -> str`

Génère la phrase de confirmation en français, 100% déterministe (templates par cas : 1 pièce / plusieurs / toutes ; 1 jour / plusieurs / tous les jours), jointure "et" dès 2 éléments. Toujours "entre le [première occurrence] et le [dernière occurrence]" — jamais les bornes brutes `start`/`end`, qui peuvent être trompeuses si peu de jours de la période matchent les `weekdays` choisis.

> Un 2e appel LLM dédié à la reformulation naturelle a été testé puis abandonné : phrasé plus administratif/long que voulu malgré les consignes.

---

## Interprétation LLM — `duplication_interpreter.py`

### `interpret_duplication_instruction(conversation, source_date, today) -> dict`

Construit le prompt (`prompts/duplication.py` + `duplication_rules.py`), appelle le LLM (`GroqClient`, même provider que `ai_heating_modification`), parse et valide la forme de la réponse (`_validate_llm_shape` — champs présents et bien typés, pas de validation métier).

**Réponse LLM attendue :**
```json
{
  "status": "ready" | "clarify" | "invalid",
  "message": "...",
  "room_ids": [...],
  "weekdays": [0-6, ...],
  "start": "YYYY-MM-DD",
  "end": "YYYY-MM-DD"
}
```

`status: "invalid"` → même comportement que `"clarify"` côté vue (message assistant ajouté, step `"clarify"`), utilisé quand l'instruction décrit plusieurs actions distinctes en une seule requête (non supporté — une seule action par requête).

### Règles d'extraction (`duplication_rules.py`)

- **Défauts silencieux** (jamais de clarification demandée) : `room_ids` omis → toutes les pièces du jour source ; `weekdays` omis → tous les jours ; `start` omis → `today + 1` (jamais `source_date + 1`, `source_date` peut être future)
- **Jamais de défaut** : `end` — absence systématique de clarification obligatoire, aucune valeur inventée
- Résolution de dates relatives ("demain", "vendredi prochain", "fin du mois prochain") calculée directement par le LLM à partir de `today` seul (une table `date_lookup` pré-calculée avait été tentée puis retirée : cassait dès qu'une date sortait de sa fenêtre)
- `source_date` n'apparaît jamais dans le prompt envoyé au LLM

---

## Serializers — `ai/api/serializers.py`

```python
class DuplicationExchangeSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()

class AiDuplicationDataSerializer(serializers.Serializer):
    room_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    weekdays = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    start = serializers.DateField(allow_null=True, required=False)
    end = serializers.DateField(allow_null=True, required=False)

class AiHeatingPlanDuplicateInputSerializer(serializers.Serializer):
    echanges = serializers.ListField(child=DuplicationExchangeSerializer(), min_length=1)
    step = serializers.ChoiceField(choices=["clarify", "to_validate", "validate"])
    source_date = serializers.DateField()
    data = AiDuplicationDataSerializer(required=False)
```

**Important :** `step` est requis à **chaque** requête (pas seulement au `validate`) — un oubli côté front renvoie un 400. `weekdays` est une liste d'**entiers** (jours ISO 0-6), pas de strings.

---

## Configuration

Aucune configuration supplémentaire — réutilise `GROQ_API_KEY` déjà en place pour `ai_heating_modification`.

**urls.py (ai) :**
```python
path("heating/duplicate/", AiHeatingPlanDuplicateView.as_view(), name="ai-heating-duplicate"),
```

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Août 2026
