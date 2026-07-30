/**
 * Dashboard Luciole — Graphiques et stats.
 */
LucioleAuth.requireAuth();

const chartDefaults = {
  responsive: true,
  plugins: { legend: { labels: { color: '#94a3b8' } } },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
    y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } },
  },
};

async function initDashboard() {
  try {
    const user = LucioleAuth.getUser();
    if (user) document.getElementById('username').textContent = user.username;

    const data = await LucioleAPI.get('/api/stats/dashboard');

    // Cartes
    document.getElementById('time-today').textContent = data.today.time_today_minutes;
    document.getElementById('sessions-today').textContent = data.today.sessions_today;
    document.getElementById('score-value').textContent = Math.round(data.score.value);
    document.getElementById('score-level').textContent = data.score.level;

    // Graphique utilisation quotidienne
    new Chart(document.getElementById('daily-chart'), {
      type: 'bar',
      data: {
        labels: data.dashboard.daily_usage.map(d => d.label),
        datasets: [{
          label: 'Minutes',
          data: data.dashboard.daily_usage.map(d => d.minutes),
          backgroundColor: 'rgba(245, 158, 11, 0.7)',
          borderRadius: 6,
        }],
      },
      options: chartDefaults,
    });

    // Évolution hebdomadaire
    new Chart(document.getElementById('weekly-chart'), {
      type: 'line',
      data: {
        labels: data.dashboard.weekly_evolution.map(w => w.week),
        datasets: [{
          label: 'Sessions',
          data: data.dashboard.weekly_evolution.map(w => w.sessions),
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true,
          tension: 0.4,
        }],
      },
      options: chartDefaults,
    });

    // Plateformes
    const platforms = data.dashboard.platforms;
    new Chart(document.getElementById('platform-chart'), {
      type: 'doughnut',
      data: {
        labels: platforms.map(p => p.name),
        datasets: [{
          data: platforms.map(p => p.minutes),
          backgroundColor: [
            '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899', '#84cc16',
          ],
        }],
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } } },
    });

    // Score history
    if (data.score_history.length) {
      new Chart(document.getElementById('score-chart'), {
        type: 'line',
        data: {
          labels: data.score_history.map(s => new Date(s.created_at).toLocaleDateString('fr-FR')),
          datasets: [{
            label: 'Score',
            data: data.score_history.map(s => s.value),
            borderColor: '#fbbf24',
            backgroundColor: 'rgba(251, 191, 36, 0.1)',
            fill: true,
            tension: 0.3,
          }],
        },
        options: chartDefaults,
      });
    }

    // Conseils
    const adviceList = document.getElementById('advice-list');
    adviceList.innerHTML = data.advice.map(a => `
      <div class="p-4 bg-slate-950 rounded-xl border-l-4 ${
        a.priority === 'high' ? 'border-red-500' : a.priority === 'medium' ? 'border-luciole-500' : 'border-green-600'
      }">
        <p class="font-medium text-sm">${a.title}</p>
        <p class="text-slate-400 text-sm mt-1">${a.message}</p>
      </div>
    `).join('');

    document.getElementById('loading').classList.add('hidden');
    document.getElementById('dashboard-content').classList.remove('hidden');
  } catch (err) {
    document.getElementById('loading').textContent = `Erreur : ${err.message}`;
  }
}

initDashboard();
