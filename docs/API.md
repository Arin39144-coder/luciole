# Documentation API — Luciole

Base URL : `http://localhost:8000` (dev) ou votre URL Render en production.

Authentification : Bearer JWT dans le header `Authorization`.

---

## Authentification

### POST `/api/auth/register`

Inscription d'un nouvel utilisateur.

**Body JSON :**
```json
{
  "username": "zo",
  "email": "zo@example.com",
  "password": "motdepasse123"
}
```

**Réponse 201 :**
```json
{
  "message": "Inscription réussie.",
  "access_token": "eyJ...",
  "user": { "id": 1, "username": "zo", "email": "zo@example.com", "created_at": "..." }
}
```

### POST `/api/auth/login`

**Body JSON :**
```json
{
  "email": "zo@example.com",
  "password": "motdepasse123"
}
```

**Réponse 200 :** même structure que register.

### GET `/api/auth/me`

🔒 Requiert JWT.

**Réponse 200 :**
```json
{ "user": { "id": 1, "username": "zo", ... } }
```

---

## Sessions IA

### POST `/api/session/start`

🔒 Démarre une session après l'overlay de réflexion.

**Body JSON :**
```json
{
  "platform_name": "ChatGPT",
  "platform_url": "chatgpt.com",
  "reason": "programmation",
  "needs_ai": "yes",
  "reflections": [
    { "question": "Pourquoi utilisez-vous l'IA ?", "answer": "Programmation" },
    { "question": "Nécessite une IA ?", "answer": "Oui" }
  ]
}
```

**Valeurs `reason` :** `etudes`, `travail`, `programmation`, `recherche`, `creativite`, `divertissement`, `autre`

**Valeurs `needs_ai` :** `yes`, `no`, `partially`

**Réponse 201 :**
```json
{
  "message": "Session démarrée.",
  "session": { "id": 42, "platform": "ChatGPT", ... },
  "score": { "value": 55.2, "level": "Utilisation consciente" },
  "today_stats": { "sessions_today": 3, "time_today_minutes": 45.0 },
  "new_badges": []
}
```

### POST `/api/session/end`

🔒 Termine une session et calcule la durée.

**Body JSON :**
```json
{ "session_id": 42 }
```

### GET `/api/session/history`

🔒 Historique paginé.

**Query params :** `page` (default 1), `per_page` (default 20, max 100)

---

## Statistiques

### GET `/api/stats/today`

🔒 Stats du jour + score + défi actuel.

### GET `/api/stats/dashboard`

🔒 Données complètes pour le dashboard (graphiques, conseils, badges, défis).

---

## Objectifs

### GET `/api/goals`

🔒 Retourne l'objectif quotidien (minutes).

### PUT `/api/goals`

🔒 Met à jour l'objectif.

**Body :** `{ "daily_limit": 90 }` (15–720 minutes)

---

## Défis & Badges

### GET `/api/challenges`

🔒 Liste des défis actifs avec progression.

### GET `/api/challenges/badges`

🔒 Badges obtenus par l'utilisateur.

---

## Santé

### GET `/health`

```json
{ "status": "ok", "service": "luciole-api" }
```

---

## Codes d'erreur

| Code | Signification |
|------|---------------|
| 400  | Validation échouée |
| 401  | Non authentifié / identifiants invalides |
| 404  | Ressource introuvable |
| 409  | Conflit (email/username existant) |
