/**
 * AgroTech API client
 * Connects to FastAPI backend at /api/v1
 */

const BASE = '/api/v1';

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  recommend: (payload) => request('POST', '/recommend', payload),
  weather:   (district, days = 15) => request('GET', `/weather/${encodeURIComponent(district)}?days=${days}`),
  growth:    (payload) => request('POST', '/growth', payload),
  taluks:    (district) => request('GET', `/location/taluks${district ? `?district=${district}` : ''}`),
  districts: () => request('GET', '/location/districts'),
  crops:     () => request('GET', '/location/crops'),
  health:    () => fetch('/health').then(r => r.json()),
};
