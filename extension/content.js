/**
 * Content Script Luciole — Overlay de réflexion sur les sites IA.
 */

(function () {
  "use strict";

  const browserAPI = typeof browser !== "undefined" ? browser : chrome;

  let currentSessionId = null;
  let overlayShown = false;
  let selectedReason = null;
  let selectedNeedsAi = null;

  function getPlatform() {
    const hostname = window.location.hostname.replace("www.", "");
    return AI_PLATFORMS[hostname] || AI_PLATFORMS[window.location.hostname] || {
      name: hostname,
      url: hostname,
    };
  }

  function shouldShowOverlay() {
    const key = `luciole_passed_${window.location.hostname}`;
    const passed = sessionStorage.getItem(key);
    return !passed;
  }

  function createOverlay(stats) {
    if (overlayShown || !shouldShowOverlay()) return;
    overlayShown = true;

    const platform = getPlatform();
    const timeToday = stats?.stats?.time_today_minutes ?? 0;
    const sessionsToday = stats?.stats?.sessions_today ?? 0;
    const dailyLimit = stats?.stats?.daily_limit_minutes ?? 120;

    const overlay = document.createElement("div");
    overlay.id = "luciole-overlay";
    overlay.innerHTML = `
      <div class="luciole-backdrop"></div>
      <div class="luciole-modal" role="dialog" aria-labelledby="luciole-title">
        <div class="luciole-header">
          <div class="luciole-logo">✦ Luciole</div>
          <div class="luciole-platform">${platform.name}</div>
        </div>

        <h1 id="luciole-title" class="luciole-title">
          Avant d'utiliser l'IA, prenez un instant.
        </h1>

        <div class="luciole-stats-row">
          <div class="luciole-stat">
            <span class="luciole-stat-value">${timeToday} min</span>
            <span class="luciole-stat-label">Temps IA aujourd'hui</span>
          </div>
          <div class="luciole-stat">
            <span class="luciole-stat-value">${sessionsToday}</span>
            <span class="luciole-stat-label">Sessions</span>
          </div>
          <div class="luciole-stat">
            <span class="luciole-stat-value">${dailyLimit} min</span>
            <span class="luciole-stat-label">Objectif quotidien</span>
          </div>
        </div>

        <div class="luciole-question-block">
          <p class="luciole-question">Pourquoi utilisez-vous l'IA maintenant ?</p>
          <div class="luciole-choices" id="luciole-reasons">
            ${REASON_OPTIONS.map(
              (r) => `<button class="luciole-choice" data-value="${r.value}">${r.label}</button>`
            ).join("")}
          </div>
        </div>

        <div class="luciole-question-block">
          <p class="luciole-question">Cette tâche nécessite-t-elle vraiment une IA ?</p>
          <div class="luciole-choices" id="luciole-needs-ai">
            ${NEEDS_AI_OPTIONS.map(
              (r) => `<button class="luciole-choice" data-value="${r.value}">${r.label}</button>`
            ).join("")}
          </div>
        </div>

        <div class="luciole-actions">
          <button class="luciole-btn luciole-btn-secondary" id="luciole-back">RETOUR</button>
          <button class="luciole-btn luciole-btn-primary" id="luciole-continue" disabled>
            CONTINUER VERS L'IA
          </button>
        </div>

        <p class="luciole-footer">Luciole — Usage conscient de l'IA</p>
      </div>
    `;

    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add("luciole-visible"));

    bindOverlayEvents(overlay, platform);
  }

  function bindOverlayEvents(overlay, platform) {
    const continueBtn = overlay.querySelector("#luciole-continue");
    const backBtn = overlay.querySelector("#luciole-back");

    overlay.querySelectorAll("#luciole-reasons .luciole-choice").forEach((btn) => {
      btn.addEventListener("click", () => {
        overlay.querySelectorAll("#luciole-reasons .luciole-choice").forEach((b) =>
          b.classList.remove("selected")
        );
        btn.classList.add("selected");
        selectedReason = btn.dataset.value;
        updateContinueButton(continueBtn);
      });
    });

    overlay.querySelectorAll("#luciole-needs-ai .luciole-choice").forEach((btn) => {
      btn.addEventListener("click", () => {
        overlay.querySelectorAll("#luciole-needs-ai .luciole-choice").forEach((b) =>
          b.classList.remove("selected")
        );
        btn.classList.add("selected");
        selectedNeedsAi = btn.dataset.value;
        updateContinueButton(continueBtn);
      });
    });

    continueBtn.addEventListener("click", async () => {
      if (!selectedReason || !selectedNeedsAi) return;

      continueBtn.disabled = true;
      continueBtn.textContent = "Chargement…";

      const reflections = [
        {
          question: "Pourquoi utilisez-vous l'IA maintenant ?",
          answer: REASON_OPTIONS.find((r) => r.value === selectedReason)?.label || selectedReason,
        },
        {
          question: "Cette tâche nécessite-t-elle vraiment une IA ?",
          answer: NEEDS_AI_OPTIONS.find((r) => r.value === selectedNeedsAi)?.label || selectedNeedsAi,
        },
      ];

      try {
        const result = await browserAPI.runtime.sendMessage({
          type: "START_SESSION",
          data: {
            platform_name: platform.name,
            platform_url: platform.url,
            reason: selectedReason,
            needs_ai: selectedNeedsAi,
            reflections,
          },
        });

        currentSessionId = result?.session?.id || result?.localSessionId;

        sessionStorage.setItem(`luciole_passed_${window.location.hostname}`, "1");
        removeOverlay(overlay);
      } catch (err) {
        console.error("[Luciole]", err);
        sessionStorage.setItem(`luciole_passed_${window.location.hostname}`, "1");
        removeOverlay(overlay);
      }
    });

    backBtn.addEventListener("click", () => {
      window.history.length > 1 ? window.history.back() : (window.location.href = "about:blank");
    });
  }

  function updateContinueButton(btn) {
    btn.disabled = !(selectedReason && selectedNeedsAi);
  }

  function removeOverlay(overlay) {
    overlay.classList.remove("luciole-visible");
    overlay.classList.add("luciole-hiding");
    setTimeout(() => overlay.remove(), 400);
    overlayShown = false;
  }

  async function init() {
    await new Promise((r) => setTimeout(r, LUCIOLE_CONFIG.OVERLAY_DELAY_MS));

    let stats = { stats: {} };
    try {
      stats = await browserAPI.runtime.sendMessage({ type: "GET_STATS" });
    } catch {
      /* mode hors-ligne */
    }

    createOverlay(stats);
  }

  // Fin de session à la fermeture de la page
  window.addEventListener("beforeunload", () => {
    if (currentSessionId) {
      browserAPI.runtime.sendMessage({
        type: "END_SESSION",
        sessionId: currentSessionId,
      });
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
