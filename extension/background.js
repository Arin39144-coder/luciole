/**
 * Service Worker Luciole — Gestion des sessions et communication API.
 */

const browserAPI = typeof browser !== "undefined" ? browser : chrome;

// Chargement de la configuration
importScripts('config.js');

// Suivi des sessions actives { tabId: { sessionId, startTime, platform } }
const activeSessions = new Map();

// ─── Gestionnaire de messages UNIQUE ──────────────────────────────
browserAPI.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender).then(sendResponse).catch((err) => {
    console.error("[Luciole]", err);
    sendResponse({ error: err.message });
  });
  return true; // Réponse asynchrone
});

// ─── Fonction principale de routage des messages ──────────────────
async function handleMessage(message, sender) {
  switch (message.type) {
    case "GET_AUTH":
      return getAuth();
    case "SET_AUTH":
      return setAuth(message.data);
    case "CLEAR_AUTH":
      return clearAuth();
    case "GET_STATS":
      return fetchStats();
    case "START_SESSION":
      return startSession(message.data, sender.tab?.id);
    case "END_SESSION":
      return endSession(message.sessionId, sender.tab?.id);
    case "GET_CONFIG":
      return { config: LUCIOLE_CONFIG };
    case "API_REQUEST":   // ⬅️ NOUVEAU : requêtes HTTP depuis la popup
      return handleApiRequest(message.data);
    default:
      return { error: "Unknown message type" };
  }
}

// ─── Gestion de l'authentification ──────────────────────────────
async function getAuth() {
  const result = await browserAPI.storage.local.get(["token", "user"]);
  return { token: result.token || null, user: result.user || null };
}

async function setAuth(data) {
  await browserAPI.storage.local.set({
    token: data.token,
    user: data.user,
  });
  return { success: true };
}

async function clearAuth() {
  await browserAPI.storage.local.remove(["token", "user"]);
  return { success: true };
}

// ─── Fonction API interne (utilisée par le service worker) ─────
async function apiRequest(endpoint, options = {}) {
  const auth = await getAuth();
  const headers = {
    "Content-Type": "application/json",
    ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${LUCIOLE_CONFIG.API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Erreur API ${response.status}`);
  }
  return data;
}

// ─── API pour la popup (via message) ─────────────────────────────
async function handleApiRequest(data) {
  const { endpoint, options = {} } = data;
  const auth = await getAuth();
  const headers = {
    "Content-Type": "application/json",
    ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
    ...options.headers,
  };
  const url = `${LUCIOLE_CONFIG.API_BASE_URL}${endpoint}`;
  console.log("[Background] Appel API vers", url);

  // Timeout de 10 secondes
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    const responseData = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(responseData.error || `Erreur ${response.status}`);
    }
    return { success: true, data: responseData };
  } catch (err) {
    clearTimeout(timeoutId);
    console.error("[Background] Erreur API détaillée :", err.name, err.message);
    return { success: false, error: err.message };
  }
}

// ─── Statistiques ────────────────────────────────────────────────
async function fetchStats() {
  try {
    const auth = await getAuth();
    if (!auth.token) return { authenticated: false };
    const data = await apiRequest("/api/stats/today");
    return { authenticated: true, ...data };
  } catch {
    return { authenticated: false };
  }
}

// ─── Gestion des sessions ──────────────────────────────────────
async function startSession(sessionData, tabId) {
  const auth = await getAuth();
  if (!auth.token) {
    return { offline: true, localSessionId: Date.now() };
  }

  const payload = {
    platform_name: sessionData.platform_name,
    platform_url: sessionData.platform_url,
    reason: sessionData.reason,
    needs_ai: sessionData.needs_ai,
    reflections: sessionData.reflections || [],
  };

  const result = await apiRequest("/api/session/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (tabId) {
    activeSessions.set(tabId, {
      sessionId: result.session.id,
      startTime: Date.now(),
      platform: sessionData.platform_name,
    });
  }

  await browserAPI.storage.local.set({
    lastStats: result.today_stats,
    lastScore: result.score,
  });

  return result;
}

async function endSession(sessionId, tabId) {
  if (!sessionId) return { skipped: true };

  try {
    const auth = await getAuth();
    if (!auth.token) return { offline: true };

    const result = await apiRequest("/api/session/end", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (tabId) activeSessions.delete(tabId);
    return result;
  } catch (err) {
    console.error("[Luciole] end session error:", err);
    return { error: err.message };
  }
}

// ─── Nettoyage des sessions à la fermeture d'un onglet ──────
if (browserAPI.tabs && browserAPI.tabs.onRemoved) {
  browserAPI.tabs.onRemoved.addListener(async (tabId) => {
    const session = activeSessions.get(tabId);
    if (session) {
      await endSession(session.sessionId, tabId);
    }
  });
}

// ─── Alarme de rappel (optionnelle) ──────────────────────────
browserAPI.alarms?.create("luciole-check", { periodInMinutes: 30 });

browserAPI.alarms?.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "luciole-check") {
    const stats = await fetchStats();
    if (stats.authenticated && stats.stats?.goal_progress_percent > 90) {
      browserAPI.notifications?.create({
        type: "basic",
        iconUrl: "assets/icon-48.png",
        title: "Luciole",
        message: "Vous approchez de votre objectif quotidien IA.",
      });
    }
  }
});