# API Luciole – Documentation des endpoints

**Version** : 1.0.0  
**Base URL** : `https://votre-backend.onrender.com/api` (ou `http://localhost:8000/api` en développement)  
**Format** : JSON

L’API utilise **JWT** pour l’authentification.  
Pour les requêtes protégées, incluez l’en-tête :
Authorization: Bearer <votre_token>

text

Toutes les erreurs renvoient un objet JSON avec une clé `"error"` et un message explicatif, accompagné d’un code HTTP approprié (400, 401, 404, 409, etc.).

---

## 1. Authentification

### `POST /auth/register` – Inscription

Crée un nouveau compte utilisateur.

**Corps (JSON)** :

| Champ      | Type   | Contraintes                       |
|------------|--------|-----------------------------------|
| `username` | string | 3–80 caractères, alphanumérique + `_` et `-` |
| `email`    | string | Email valide                      |
| `password` | string | Minimum 8 caractères              |

**Exemple de requête** :

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "monMotDePasse123"
}
Réponse (201 Created) :

json
{
  "message": "Inscription réussie.",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-07-30T10:00:00Z"
  }
}
POST /auth/login – Connexion
Authentifie un utilisateur existant.

Corps (JSON) :

Champ	Type
email	string
password	string
Exemple :

json
{
  "email": "alice@example.com",
  "password": "monMotDePasse123"
}
Réponse (200 OK) : identique à l’inscription.

GET /auth/me – Profil utilisateur (protégé)
Retourne les informations de l’utilisateur connecté.

Réponse (200 OK) :

json
{
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-07-30T10:00:00Z"
  }
}
2. Sessions IA
POST /session/start – Démarrer une session (protégé)
Enregistre le début d’une utilisation d’IA.

Corps (JSON) :

Champ	Type	Contraintes
platform_name	string	Nom de la plateforme (ex: "ChatGPT")
platform_url	string	URL du site (ex: "chat.openai.com")
reason	string	Une des valeurs : etudes, travail, programmation, recherche, creativite, divertissement, autre
needs_ai	string	yes, no ou partially
reflections	array	(Optionnel) Liste d’objets { "question": string, "answer": string }
Exemple :

json
{
  "platform_name": "ChatGPT",
  "platform_url": "chat.openai.com",
  "reason": "programmation",
  "needs_ai": "yes",
  "reflections": [
    { "question": "Pourquoi utilisez-vous l'IA maintenant ?", "answer": "Programmation" },
    { "question": "Cette tâche nécessite-t-elle vraiment une IA ?", "answer": "Oui" }
  ]
}
Réponse (201 Created) :

json
{
  "message": "Session démarrée.",
  "session": {
    "id": 42,
    "user_id": 1,
    "platform": "ChatGPT",
    "platform_id": 3,
    "start_time": "2026-07-30T10:05:00Z",
    "end_time": null,
    "duration": null,
    "duration_minutes": null,
    "reason": "programmation",
    "needs_ai": "yes"
  },
  "score": {
    "id": 1,
    "value": 55.3,
    "level": "Utilisation consciente",
    "created_at": "2026-07-30T10:05:00Z"
  },
  "today_stats": {
    "sessions_today": 2,
    "time_today_seconds": 180,
    "time_today_minutes": 3.0,
    "daily_limit_minutes": 120,
    "goal_progress_percent": 2.5
  },
  "new_badges": ["Premier pas"]
}
POST /session/end – Terminer une session (protégé)
Ferme une session en cours.

Corps (JSON) :

Champ	Type
session_id	entier
Exemple :

json
{
  "session_id": 42
}
Réponse (200 OK) :

json
{
  "message": "Session terminée.",
  "session": {
    "id": 42,
    "duration": 300,
    "duration_minutes": 5.0,
    "end_time": "2026-07-30T10:10:00Z",
    ...
  },
  "score": { ... }
}
GET /session/history – Historique des sessions (protégé)
Retourne la liste paginée des sessions de l’utilisateur.

Paramètres (query string) :

Nom	Type	Défaut	Description
page	entier	1	Numéro de page
per_page	entier	20	Nombre d’éléments par page (max 100)
Exemple : GET /api/session/history?page=2&per_page=10

Réponse (200 OK) :

json
{
  "sessions": [
    {
      "id": 42,
      "platform": "ChatGPT",
      "start_time": "2026-07-30T10:05:00Z",
      "end_time": "2026-07-30T10:10:00Z",
      "duration": 300,
      "duration_minutes": 5.0,
      "reason": "programmation",
      "needs_ai": "yes"
    },
    ...
  ],
  "total": 45,
  "pages": 5,
  "current_page": 2
}
3. Statistiques
GET /stats/today – Résumé du jour (protégé)
Donne les statistiques du jour pour l’utilisateur connecté.

Réponse (200 OK) :

json
{
  "stats": {
    "sessions_today": 3,
    "time_today_seconds": 900,
    "time_today_minutes": 15.0,
    "daily_limit_minutes": 120,
    "goal_progress_percent": 12.5
  },
  "score": {
    "id": 5,
    "value": 62.0,
    "level": "Utilisation réfléchie",
    "created_at": "2026-07-30T09:00:00Z"
  },
  "current_challenge": {
    "id": 1,
    "challenge": {
      "id": 2,
      "title": "Réduction 10%",
      "description": "Réduire son temps IA de 10% par rapport à hier",
      "type": "daily",
      "reward": 20,
      "active": true
    },
    "completed": false,
    "started_at": "2026-07-30T00:00:00Z",
    "completed_at": null
  }
}
GET /stats/dashboard – Tableau de bord complet (protégé)
Retourne toutes les données nécessaires pour afficher le dashboard : statistiques, historique des scores, conseils, badges, défis.

Réponse (200 OK) :

json
{
  "today": { ... },                       // identique à /stats/today
  "dashboard": {
    "daily_usage": [
      { "date": "2026-07-24", "label": "Lun", "minutes": 12.5, "sessions": 2 },
      { "date": "2026-07-25", "label": "Mar", "minutes": 8.0, "sessions": 1 },
      ...
    ],
    "weekly_evolution": [
      { "week": "S-3", "sessions": 10 },
      { "week": "S-2", "sessions": 8 },
      { "week": "S-1", "sessions": 5 },
      { "week": "Cette semaine", "sessions": 7 }
    ],
    "platforms": [
      { "name": "ChatGPT", "sessions": 12, "minutes": 45.2 },
      { "name": "Claude", "sessions": 5, "minutes": 18.5 }
    ]
  },
  "score": { ... },
  "score_history": [
    { "value": 55, "created_at": "2026-07-20T...", "level": "Utilisation consciente" },
    { "value": 62, "created_at": "2026-07-21T...", "level": "Utilisation réfléchie" },
    ...
  ],
  "advice": [
    {
      "type": "batching",
      "title": "Regroupez vos demandes",
      "message": "Vous avez beaucoup de sessions courtes. Essayez de regrouper vos questions en une seule session.",
      "priority": "medium"
    },
    ...
  ],
  "badges": [
    {
      "badge": { "name": "Premier pas", "description": "Première session enregistrée avec réflexion", "icon": "star" },
      "earned_at": "2026-07-30T10:05:00Z"
    }
  ],
  "challenges": [
    {
      "id": 1,
      "title": "Réflexion 24h",
      "description": "Réfléchir avant chaque utilisation pendant 24h",
      "type": "daily",
      "reward": 15,
      "completed": false,
      "user_progress": { ... }
    }
  ]
}
4. Objectifs
GET /goals – Objectif quotidien (protégé)
Retourne l’objectif de temps quotidien (en minutes).

Réponse (200 OK) :

json
{
  "goal": {
    "id": 1,
    "user_id": 1,
    "daily_limit": 120,
    "daily_limit_hours": 2.0
  }
}
PUT /goals – Mettre à jour l’objectif (protégé)
Modifie la limite quotidienne.

Corps (JSON) :

Champ	Type	Contrainte
daily_limit	entier	Entre 15 et 720 (minutes)
Exemple :

json
{
  "daily_limit": 90
}
Réponse (200 OK) :

json
{
  "message": "Objectif mis à jour.",
  "goal": { ... }
}
5. Défis et badges
GET /challenges – Liste des défis (protégé)
Retourne tous les défis disponibles avec leur état de progression pour l’utilisateur.

Réponse (200 OK) :

json
{
  "challenges": [
    {
      "id": 1,
      "title": "Réflexion 24h",
      "description": "Réfléchir avant chaque utilisation pendant 24h",
      "type": "daily",
      "reward": 15,
      "active": true,
      "completed": false,
      "user_progress": {
        "id": 3,
        "user_id": 1,
        "challenge_id": 1,
        "completed": false,
        "started_at": "2026-07-30T00:00:00Z",
        "completed_at": null
      }
    },
    ...
  ]
}
GET /challenges/badges – Badges obtenus (protégé)
Liste les badges déjà déverrouillés par l’utilisateur.

Réponse (200 OK) :

json
{
  "badges": [
    {
      "badge": {
        "name": "Premier pas",
        "description": "Première session enregistrée avec réflexion",
        "icon": "star"
      },
      "earned_at": "2026-07-30T10:05:00Z"
    },
    ...
  ]
}
6. Santé
GET /health – Vérification du service
Réponse (200 OK) :

json
{
  "status": "ok",
  "service": "luciole-api"
}
Codes d’erreur courants
Code	Signification
400	Requête invalide (champ manquant ou mal formaté)
401	Authentification requise ou token invalide
404	Ressource non trouvée
409	Conflit (ex: email déjà utilisé)
500	Erreur interne du serveur

