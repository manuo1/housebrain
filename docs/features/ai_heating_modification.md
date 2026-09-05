# AI Heating Modification - Modification IA des plannings

Feature permettant de modifier les plannings de chauffage en langage naturel via un LLM.

---

## Vue d'ensemble

L'utilisateur saisit une instruction en langage naturel (français ou anglais) dans une zone de texte intégrée à la page de planning. Le backend envoie cette instruction accompagnée du plan courant à un LLM, qui retourne le plan modifié. La modification est intégrée dans l'historique d'annulation existant, exactement comme une modification manuelle.

**Exemples d'instructions :**
- "Allume le chauffage de la chambre R de 10h à 12h à 21 degrés"
- "Éteins le chauffage de toutes les pièces pendant 1 heure"
- "Augmente de 2°C toutes les pièces ce soir"

---

## Flux complet

```
User saisit instruction
→ AiPlanInput.onSubmit()
→ applyAiPlanModification(instruction, plan courant)
→ POST /api/ai/heating/modify/
→ Django valide l'input (serializer)
→ plan_modifier.modify_heating_plan()
→ Groq LLM génère le plan modifié
→ Validation du plan retourné (SchedulePattern.clean())
→ Retour du plan au frontend
→ applyChange(newPlan)
→ Plan inséré dans l'historique undo
→ Timeline mise à jour
```

---

## Intégration dans l'historique d'annulation

La modification IA passe par le même `applyChange()` que les modifications manuelles. Elle est donc :
- **Visible** immédiatement dans la timeline
- **Annulable** via le bouton Annuler (undo progressif)
- **Non sauvegardée** tant que l'utilisateur ne clique pas sur Enregistrer

L'utilisateur peut donc :
1. Modifier manuellement le planning
2. Demander une modification IA
3. Voir le résultat
4. Annuler si insatisfait
5. Sauvegarder quand satisfait

---

## LLM Provider

**Provider actuel :** Groq (`openai/gpt-oss-120b`)

**Architecture extensible :** L'interface abstraite `LLMClient` permet de changer de provider sans modifier la logique métier.

**Limitations du plan gratuit Groq (par modèle, tier gratuit sans carte bancaire) :**
- 30 requêtes/minute, 1 000 requêtes/jour
- 8 000 tokens/minute, 200 000 tokens/jour
- Largement suffisant pour un usage personnel ponctuel (quelques modifications de planning par jour) ; à surveiller uniquement si une requête unique (prompt système + plan JSON complet + réponse) approchait les 8 000 tokens

---

## Références

- **Backend :** `docs/backend/ai_heating_modification.md`
- **Frontend :** `docs/frontend/ai_heating_modification.md`

---

Auteur : Emmanuel Oudot
Dernière mise à jour : Juillet 2026
