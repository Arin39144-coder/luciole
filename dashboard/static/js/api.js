/**
 * Client API Luciole Dashboard
 */
const LucioleAPI = {
  baseURL: window.location.origin,

  async request(method, endpoint, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = LucioleAuth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`${this.baseURL}${endpoint}`, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || `Erreur ${response.status}`);
    }
    return data;
  },

  get(endpoint) { return this.request('GET', endpoint); },
  post(endpoint, body) { return this.request('POST', endpoint, body); },
  put(endpoint, body) { return this.request('PUT', endpoint, body); },

  login(email, password) {
    return this.post('/api/auth/login', { email, password });
  },

  register(username, email, password) {
    return this.post('/api/auth/register', { username, email, password });
  },
};
