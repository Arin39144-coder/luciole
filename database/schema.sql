-- Luciole — Schéma MySQL
-- Compatible MySQL 8.0+ / Aiven

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS luciole
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE luciole;

-- ─── Utilisateurs ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(80)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Plateformes IA ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_platforms (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80)  NOT NULL UNIQUE,
    url  VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Sessions IA ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_sessions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    platform_id INT          NOT NULL,
    start_time  DATETIME     NOT NULL,
    end_time    DATETIME     NULL,
    duration    INT          NULL COMMENT 'Durée en secondes',
    reason      VARCHAR(50)  NULL,
    needs_ai    VARCHAR(20)  NULL COMMENT 'yes | no | partially',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)     REFERENCES users(id)         ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES ai_platforms(id) ON DELETE RESTRICT,
    INDEX idx_sessions_user_date (user_id, start_time),
    INDEX idx_sessions_platform (platform_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Objectifs utilisateur ──────────────────────────────────
CREATE TABLE IF NOT EXISTS user_goals (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    daily_limit INT NOT NULL DEFAULT 120 COMMENT 'Limite quotidienne en minutes',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Défis ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS challenges (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(120) NOT NULL,
    description TEXT         NOT NULL,
    type        VARCHAR(50)  NOT NULL COMMENT 'daily | weekly | milestone',
    reward      INT          NOT NULL DEFAULT 10,
    active      TINYINT(1)   NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Défis utilisateur ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_challenges (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT         NOT NULL,
    challenge_id INT         NOT NULL,
    completed    TINYINT(1)  NOT NULL DEFAULT 0,
    started_at   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME    NULL,
    FOREIGN KEY (user_id)      REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_challenge (user_id, challenge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Badges ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS badges (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(80)  NOT NULL UNIQUE,
    description TEXT         NOT NULL,
    icon        VARCHAR(50)  NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Badges utilisateur ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_badges (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id   INT      NOT NULL,
    badge_id  INT      NOT NULL,
    earned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_badge (user_id, badge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Réponses de réflexion ────────────────────────────────────
CREATE TABLE IF NOT EXISTS reflection_answers (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT          NOT NULL,
    question   VARCHAR(255) NOT NULL,
    answer     VARCHAR(255) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES ai_sessions(id) ON DELETE CASCADE,
    INDEX idx_reflection_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Scores ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scores (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT   NOT NULL,
    value      FLOAT NOT NULL,
    level      VARCHAR(50) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_scores_user_date (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── Données initiales ────────────────────────────────────────
INSERT INTO ai_platforms (name, url) VALUES
    ('ChatGPT',    'chat.openai.com'),
    ('ChatGPT',    'chatgpt.com'),
    ('Claude',     'claude.ai'),
    ('Gemini',     'gemini.google.com'),
    ('Copilot',    'copilot.microsoft.com'),
    ('Perplexity', 'perplexity.ai'),
    ('Poe',        'poe.com'),
    ('DeepSeek',   'deepseek.com')
ON DUPLICATE KEY UPDATE url = VALUES(url);

INSERT INTO challenges (title, description, type, reward) VALUES
    ('Réflexion 24h', 'Réfléchir avant chaque utilisation pendant 24h', 'daily', 15),
    ('Réduction 10%', 'Réduire son temps IA de 10% par rapport à hier', 'daily', 20),
    ('Semaine consciente', 'Utiliser l''IA de façon consciente pendant 7 jours', 'weekly', 50),
    ('Pause nocturne', 'Éviter l''IA entre 22h et 7h pendant 3 jours', 'weekly', 30)
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO badges (name, description, icon) VALUES
    ('Premier pas', 'Première session enregistrée avec réflexion', 'star'),
    ('3 jours conscients', '3 jours consécutifs avec score > 40', 'calendar'),
    ('Une semaine maîtrisée', '7 jours consécutifs avec score > 60', 'trophy'),
    ('Réduction 50%', 'Réduction de 50% du temps IA sur une semaine', 'leaf'),
    ('Utilisateur réfléchi', 'Score supérieur à 80 pendant 5 jours', 'brain')
ON DUPLICATE KEY UPDATE description = VALUES(description);

SET FOREIGN_KEY_CHECKS = 1;
