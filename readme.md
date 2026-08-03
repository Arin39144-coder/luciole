# ✦ Luciole – Compagnon numérique pour un usage conscient de l’IA



Luciole est une extension de navigateur (Chrome et Firefox) couplée à un backend API et un tableau de bord web. Elle vous aide à prendre conscience de votre utilisation des intelligences artificielles (ChatGPT, Claude, Gemini, Copilot, Perplexity, etc.) en vous proposant un **moment de réflexion** avant chaque session. Ce n’est pas un bloqueur, mais un outil de sensibilisation.

## Fonctionnalités

- **Overlay de réflexion** sur les sites IA (question sur le motif et la nécessité de l’IA)
- **Suivi des sessions** (durée, plateforme, raison, besoin réel)
- **Score de réflexion** (0–100) basé sur vos habitudes
- **Objectifs quotidiens** (limite de temps personnalisable)
- **Défis et badges** pour ancrer de meilleures pratiques
- **Dashboard web** avec statistiques et graphiques
- **Extension légère** pour Chrome et Firefox (Manifest V3)

## Architecture
luciole/
├── extension/ # Extension Chrome / Firefox
├── backend/ # API Flask
├── dashboard/ # Interface web (HTML + Tailwind + Chart.js)
├── database/ # Schéma MySQL
├── docker-compose.yml
├── .env.example
└── README.md

text

## Technologies et matériel 
- Python 3.11+
- Aiven MySQL, Firefox
- railway(déploiement)
- Docker & Docker Compose
- Navigateur Chrome ou Firefox

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/arin39144-coder/luciole.git
cd luciole
