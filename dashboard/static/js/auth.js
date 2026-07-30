/**
 * Gestion de l'authentification côté dashboard.
 */
const LucioleAuth = {
  TOKEN_KEY: 'luciole_token',
  USER_KEY: 'luciole_user',

  setToken(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    if (user) localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  },

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  getUser() {
    const raw = localStorage.getItem(this.USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },

  clear() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  },

  requireAuth() {
    if (!this.getToken()) {
      window.location.href = '/login';
    }
  },
};

document.getElementById('logout-btn')?.addEventListener('click', () => {
  LucioleAuth.clear();
  window.location.href = '/login';
});
