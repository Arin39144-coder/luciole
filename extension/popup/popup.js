/**
 * Popup Luciole — Auth et stats rapides.
 */

const browserAPI = typeof browser !== "undefined" ? browser : chrome;

const screens = {
  loading: document.getElementById("loading"),
  auth: document.getElementById("auth-screen"),
  dashboard: document.getElementById("dashboard-screen"),
};

function showScreen(name) {
  Object.values(screens).forEach((s) => s.classList.add("hidden"));
  screens[name]?.classList.remove("hidden");
}

// Supprimez l'ancienne fonction apiRequest qui faisait fetch directement
// et remplacez-la par :

async function apiRequest(endpoint, options = {}) {
  console.log("apiRequest appelé pour", endpoint);
  const result = await browserAPI.runtime.sendMessage({
    type: "API_REQUEST",
    data: { endpoint, options }
  });
  console.log("Réponse du background :", result);
  if (!result.success) {
    throw new Error(result.error);
  }
  return result.data;
}

// Tabs connexion / inscription
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    const isLogin = tab.dataset.tab === "login";
    document.getElementById("login-form").classList.toggle("hidden", !isLogin);
    document.getElementById("register-form").classList.toggle("hidden", isLogin);
    document.getElementById("auth-error").classList.add("hidden");
  });
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  console.log("Tentative de connexion...");
  const errorEl = document.getElementById("auth-error");
  errorEl.classList.add("hidden");

  try {
    const data = await apiRequest("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: document.getElementById("login-email").value,
        password: document.getElementById("login-password").value,
      }),
    });

    await browserAPI.runtime.sendMessage({
      type: "SET_AUTH",
      data: { token: data.access_token, user: data.user },
    });

    await loadDashboard(data.user);
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove("hidden");
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errorEl = document.getElementById("auth-error");
  errorEl.classList.add("hidden");

  try {
    const data = await apiRequest("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username: document.getElementById("register-username").value,
        email: document.getElementById("register-email").value,
        password: document.getElementById("register-password").value,
      }),
    });

    await browserAPI.runtime.sendMessage({
      type: "SET_AUTH",
      data: { token: data.access_token, user: data.user },
    });

    await loadDashboard(data.user);
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove("hidden");
  }
});

document.getElementById("logout-btn").addEventListener("click", async () => {
  await browserAPI.runtime.sendMessage({ type: "CLEAR_AUTH" });
  showScreen("auth");
});

document.getElementById("open-dashboard").addEventListener("click", () => {
  browserAPI.tabs.create({ url: LUCIOLE_CONFIG.DASHBOARD_URL });
});

async function loadDashboard(user) {
  showScreen("dashboard");
  document.getElementById("username").textContent = user.username;

  try {
    const stats = await browserAPI.runtime.sendMessage({ type: "GET_STATS" });
    if (stats.score) {
      document.getElementById("score-value").textContent = Math.round(stats.score.value);
      document.getElementById("score-level").textContent = stats.score.level;
    }
    if (stats.stats) {
      document.getElementById("time-today").textContent = stats.stats.time_today_minutes || 0;
      document.getElementById("sessions-today").textContent = stats.stats.sessions_today || 0;
    }
    if (stats.current_challenge?.challenge) {
      document.getElementById("challenge-title").textContent =
        stats.current_challenge.challenge.title;
    } else {
      document.getElementById("challenge-card").classList.add("hidden");
    }
  } catch {
    /* stats optionnelles */
  }
}

async function init() {
  const auth = await browserAPI.runtime.sendMessage({ type: "GET_AUTH" });
  if (auth.token && auth.user) {
    await loadDashboard(auth.user);
  } else {
    showScreen("auth");
  }
}

init();
