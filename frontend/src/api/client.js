const API_BASE = '/api';

export async function apiRequest(endpoint, method = 'GET', body = null) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const config = { method, headers };
  if (body) config.body = JSON.stringify(body);

  let res;
  try {
    res = await fetch(`${API_BASE}${endpoint}`, config);
  } catch (netErr) {
    throw new Error('Unable to connect to the SubscriptIQ server. Please verify the service is running.');
  }

  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    let detailMsg = 'Session expired or invalid credentials.';
    try {
      const errText = await res.text();
      const parsed = JSON.parse(errText);
      if (parsed?.detail) detailMsg = parsed.detail;
    } catch (_) {}

    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw new Error(detailMsg);
  }

  if (res.status === 204) {
    return null;
  }

  let data = null;
  const rawText = await res.text().catch(() => '');
  if (rawText && rawText.trim().length > 0) {
    try {
      data = JSON.parse(rawText);
    } catch (_) {
      if (!res.ok) {
        throw new Error(`Server error (${res.status}): ${res.statusText || 'Unexpected server response'}`);
      }
      return rawText;
    }
  }

  if (!res.ok) {
    const detail = data?.detail;
    const msg = typeof detail === 'string' 
      ? detail 
      : Array.isArray(detail) 
        ? detail.map(d => d.msg || JSON.stringify(d)).join(', ')
        : `Request failed with status ${res.status}`;
    throw new Error(msg);
  }

  return data;
}