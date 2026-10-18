import React, { useState, useEffect } from 'react';
import { useDistricts } from '../hooks/useAgrotech';
import { api } from '../utils/api';

const HORIZONS = [7, 15, 30, 45, 60];

const RISK_CONFIG = {
  'High': { bg: 'rgba(239, 68, 68, 0.12)', border: 'rgba(239, 68, 68, 0.35)', color: '#f87171', icon: '🌧️' },
  'Moderate': { bg: 'rgba(245, 158, 11, 0.12)', border: 'rgba(245, 158, 11, 0.35)', color: '#fbbf24', icon: '🌦️' },
  'Low': { bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.25)', color: '#4ade80', icon: '☀️' },
};

export function WeatherPage() {
  const districts = useDistricts();
  const [district, setDistrict] = useState('Davanagere');
  const [days, setDays] = useState(15);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeather = (dist, horizon) => {
    if (!dist) return;
    setLoading(true);
    setError(null);
    api.weather(dist, horizon)
      .then(setForecast)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (districts.length > 0 && !district) {
      setDistrict(districts[0]);
      fetchWeather(districts[0], days);
    } else if (district) {
      fetchWeather(district, days);
    }
  }, [district, days]);

  const summary = forecast?.summary || {};
  const dayList = forecast?.days || [];

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1.5rem 4rem' }}>
      
      {/* Page Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.4rem' }}>
          <span className="badge badge-sky">Module 3 · Time-Series ML</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>34-Year Climate Reanalysis · Karnataka IMD</span>
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, margin: '0 0 0.5rem 0', letterSpacing: '-0.02em' }}>
          District Agro-Weather Forecasting
        </h1>
        <p style={{ margin: 0, fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', lineHeight: 1.5 }}>
          Multi-horizon rainfall probability and temperature predictions calibrated specifically for agricultural dry-spell
          and irrigation management.
        </p>
      </div>

      {/* Control Bar */}
      <div className="card glass-card" style={{ padding: '1.25rem 1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'center' }}>
          <div style={{ minWidth: '220px', flex: 1 }}>
            <label className="form-label">Select Karnataka District</label>
            <select
              className="form-select"
              value={district}
              onChange={e => setDistrict(e.target.value)}
            >
              {districts.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="form-label">Forecast Horizon</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {HORIZONS.map(h => (
                <button
                  key={h}
                  onClick={() => setDays(h)}
                  className={`btn ${days === h ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ padding: '0.45rem 0.9rem', fontSize: '0.88rem' }}
                >
                  +{h} Days
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Loading & Error States */}
      {loading && (
        <div className="card glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <div className="spinner" style={{ width: 40, height: 40, margin: '0 auto 1rem', borderWidth: 3 }}></div>
          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>
            Generating {days}-day predictive meteorological trajectory for {district}…
          </p>
        </div>
      )}

      {error && (
        <div className="card" style={{ padding: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.08)' }}>
          <div style={{ color: '#fca5a5', fontWeight: 600 }}>Failed to fetch weather forecast</div>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{error}</div>
        </div>
      )}

      {/* Forecast Data Content */}
      {!loading && forecast && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Summary KPIs */}
          <div className="grid-3">
            <div className="card" style={{ padding: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Mean Rain Probability
              </div>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--sky-400)', marginTop: '0.3rem' }}>
                {summary.avg_rain_probability_pct ?? 0}%
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Calculated over next {days} days
              </div>
            </div>

            <div className="card" style={{ padding: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Total Expected Rainfall
              </div>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--sky-400)', marginTop: '0.3rem' }}>
                {summary.total_expected_rain_mm ?? 0} <span style={{ fontSize: '1.2rem', fontWeight: 500 }}>mm</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                High rain days: {summary.high_rain_risk_days ?? 0}
              </div>
            </div>

            <div className="card" style={{ padding: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Agronomic Irrigation Advice
              </div>
              <div style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginTop: '0.5rem', lineHeight: 1.5 }}>
                {summary.irrigation_advisory || 'Soil moisture sufficient for standard cultivation.'}
              </div>
            </div>
          </div>

          {/* Daily Forecast Cards Grid */}
          <div>
            <div className="section-title">
              <div className="icon">🌦️</div>
              <div>
                <h2 style={{ margin: 0 }}>{district} · Daily Outlook</h2>
                <p style={{ margin: 0, fontSize: '0.85rem' }}>
                  Horizon sequence starting from {forecast.forecast_from}
                </p>
              </div>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
              gap: '1rem'
            }}>
              {dayList.map((d, i) => {
                const conf = RISK_CONFIG[d.rain_risk] || RISK_CONFIG['Low'];
                return (
                  <div
                    key={i}
                    className="card"
                    style={{
                      padding: '1rem 0.8rem',
                      textAlign: 'center',
                      background: conf.bg,
                      border: `1px solid ${conf.border}`,
                      transition: 'transform 0.15s ease',
                    }}
                  >
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                      {new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', weekday: 'short' })}
                    </div>
                    <div style={{ fontSize: '1.8rem', margin: '0.4rem 0' }}>
                      {conf.icon}
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: conf.color }}>
                      {d.rain_probability_pct}%
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Rain chance
                    </div>

                    <div style={{ margin: '0.6rem 0', borderTop: '1px solid var(--border)', paddingTop: '0.4rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--sky-400)' }}>
                        {d.expected_rain_mm} mm
                      </div>
                      {d.temp_max_c && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                          {d.temp_min_c}° - {d.temp_max_c}°C
                        </div>
                      )}
                    </div>

                    <span
                      className="badge"
                      style={{
                        background: conf.border,
                        color: conf.color,
                        fontSize: '0.68rem',
                        padding: '0.2rem 0.5rem'
                      }}
                    >
                      {d.rain_risk} Risk
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
