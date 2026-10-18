import React, { useState } from 'react';
import { useDistricts, useTaluks } from '../hooks/useAgrotech';

const SEASONS = ['Kharif', 'Rabi', 'Summer'];

export function RecommendForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    district: '',
    taluk: '',
    season: 'Kharif',
    N: '', P: '', K: '', ph: '',
    temperature: '', humidity: '', rainfall: '',
    sow_date: '',
    top_n: 5,
  });
  const [showSoil,    setShowSoil]    = useState(false);
  const [showWeather, setShowWeather] = useState(false);

  const districts = useDistricts();
  const taluks    = useTaluks(form.district);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      district: form.district || undefined,
      taluk:    form.taluk    || undefined,
      season:   form.season,
      top_n:    form.top_n,
    };
    if (form.N)   payload.N   = parseFloat(form.N);
    if (form.P)   payload.P   = parseFloat(form.P);
    if (form.K)   payload.K   = parseFloat(form.K);
    if (form.ph)  payload.ph  = parseFloat(form.ph);
    if (form.temperature) payload.temperature = parseFloat(form.temperature);
    if (form.humidity)    payload.humidity    = parseFloat(form.humidity);
    if (form.rainfall)    payload.rainfall    = parseFloat(form.rainfall);
    if (form.sow_date)    payload.sow_date    = form.sow_date;
    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {/* Location */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <div className="card-header">
          <span className="card-icon">📍</span>
          <h3 style={{ margin: 0 }}>Location</h3>
        </div>
        <div className="grid-2">
          <div className="form-group">
            <label className="form-label">District *</label>
            <select className="form-select" value={form.district}
              onChange={e => { set('district', e.target.value); set('taluk', ''); }} required>
              <option value="">Select district…</option>
              {districts.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Taluk (optional)</label>
            <select className="form-select" value={form.taluk} onChange={e => set('taluk', e.target.value)}>
              <option value="">Any taluk</option>
              {taluks.map(t => <option key={t.taluk} value={t.taluk}>{t.taluk}</option>)}
            </select>
          </div>
        </div>
        <div className="grid-2" style={{ marginTop: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Season</label>
            <select className="form-select" value={form.season} onChange={e => set('season', e.target.value)}>
              {SEASONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Sowing Date (optional)</label>
            <input type="date" className="form-input" value={form.sow_date}
              onChange={e => set('sow_date', e.target.value)} />
          </div>
        </div>
      </div>

      {/* Soil */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <div className="card-header" style={{ cursor: 'pointer', marginBottom: 0 }}
          onClick={() => setShowSoil(!showSoil)}>
          <span className="card-icon">🧪</span>
          <h3 style={{ margin: 0, flex: 1 }}>Soil Health Card Values</h3>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            {showSoil ? 'Hide' : 'Enter values (optional)'}
          </span>
        </div>
        {!showSoil && (
          <p style={{ marginTop: '0.75rem', fontSize: '0.85rem' }}>
            Leave blank to use agro-zone medians automatically.
          </p>
        )}
        {showSoil && (
          <div className="grid-4" style={{ marginTop: '1rem' }}>
            {[
              { key: 'N',  label: 'Nitrogen (N)',    unit: 'kg/ha', min: 0, max: 200 },
              { key: 'P',  label: 'Phosphorus (P)',  unit: 'kg/ha', min: 0, max: 150 },
              { key: 'K',  label: 'Potassium (K)',   unit: 'kg/ha', min: 0, max: 150 },
              { key: 'ph', label: 'Soil pH',         unit: '',      min: 3, max: 10 },
            ].map(({ key, label, unit, min, max }) => (
              <div key={key} className="form-group">
                <label className="form-label">{label} {unit && <span style={{ opacity: 0.6 }}>({unit})</span>}</label>
                <input type="number" className="form-input" placeholder="Auto"
                  min={min} max={max} step="0.1"
                  value={form[key]} onChange={e => set(key, e.target.value)} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Weather */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <div className="card-header" style={{ cursor: 'pointer', marginBottom: 0 }}
          onClick={() => setShowWeather(!showWeather)}>
          <span className="card-icon">🌦️</span>
          <h3 style={{ margin: 0, flex: 1 }}>Override Weather</h3>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            {showWeather ? 'Hide' : 'Optional – uses historical data if left blank'}
          </span>
        </div>
        {showWeather && (
          <div className="grid-3" style={{ marginTop: '1rem' }}>
            {[
              { key: 'temperature', label: 'Avg Temperature', unit: '°C',  min: -5,  max: 55 },
              { key: 'humidity',    label: 'Humidity',         unit: '%',   min: 0,   max: 100 },
              { key: 'rainfall',    label: 'Monthly Rainfall', unit: 'mm',  min: 0,   max: 800 },
            ].map(({ key, label, unit, min, max }) => (
              <div key={key} className="form-group">
                <label className="form-label">{label} <span style={{ opacity: 0.6 }}>({unit})</span></label>
                <input type="number" className="form-input" placeholder="Auto"
                  min={min} max={max} step="0.1"
                  value={form[key]} onChange={e => set(key, e.target.value)} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Number of crops */}
      <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '1rem' }}>
        <label className="form-label" style={{ whiteSpace: 'nowrap' }}>Show top</label>
        <input type="range" min={1} max={10} value={form.top_n}
          onChange={e => set('top_n', parseInt(e.target.value))}
          style={{ flex: 1, accentColor: 'var(--green-500)' }} />
        <span style={{ minWidth: '2rem', color: 'var(--green-400)', fontWeight: 600 }}>{form.top_n}</span>
        <label className="form-label">crops</label>
      </div>

      <button type="submit" className="btn btn-primary btn-lg" disabled={loading || !form.district}>
        {loading ? (
          <>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
              style={{ animation: 'spin 1s linear infinite' }}>
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="30 60"
                strokeLinecap="round" />
            </svg>
            Analysing…
          </>
        ) : (
          <>🌱 Get Crop Recommendations</>
        )}
      </button>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </form>
  );
}
