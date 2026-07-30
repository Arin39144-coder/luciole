/**
 * Configuration Luciole — Modifier l'URL API pour la production.
 */
const LUCIOLE_CONFIG = {
  API_BASE_URL: "http://localhost:8000",
  DASHBOARD_URL: "http://localhost:8000/dashboard",
  OVERLAY_DELAY_MS: 300,
  SESSION_TRACKING_INTERVAL_MS: 60000,
};

// Plateformes IA détectées
const AI_PLATFORMS = {
  "chat.openai.com": { name: "ChatGPT", url: "chat.openai.com" },
  "chatgpt.com": { name: "ChatGPT", url: "chatgpt.com" },
  "claude.ai": { name: "Claude", url: "claude.ai" },
  "gemini.google.com": { name: "Gemini", url: "gemini.google.com" },
  "copilot.microsoft.com": { name: "Copilot", url: "copilot.microsoft.com" },
  "perplexity.ai": { name: "Perplexity", url: "perplexity.ai" },
  "www.perplexity.ai": { name: "Perplexity", url: "perplexity.ai" },
  "poe.com": { name: "Poe", url: "poe.com" },
  "chat.deepseek.com": { name: "DeepSeek", url: "deepseek.com" },
  "www.deepseek.com": { name: "DeepSeek", url: "deepseek.com" },
};

const REASON_OPTIONS = [
  { value: "etudes", label: "Études" },
  { value: "travail", label: "Travail" },
  { value: "programmation", label: "Programmation" },
  { value: "recherche", label: "Recherche" },
  { value: "creativite", label: "Créativité" },
  { value: "divertissement", label: "Divertissement" },
  { value: "autre", label: "Autre" },
];

const NEEDS_AI_OPTIONS = [
  { value: "yes", label: "Oui" },
  { value: "no", label: "Non" },
  { value: "partially", label: "Partiellement" },
];
