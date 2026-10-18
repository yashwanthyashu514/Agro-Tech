import React, { useState, useEffect } from 'react';
import { useDistricts } from '../hooks/useAgrotech';
import { api } from '../utils/api';

const HORIZONS = [7, 15, 30, 45, 60];

const RISK_CONFIG = {
  'High':     { bg: 'rgba(239,68,68,0.12)',   border: 'rgba(239,68,68,0.35)',    color: '#f87171', icon: '🌧️', label: 'High Rain' },
  'Moderate': { bg: 'rgba(245,158,11,0.12)',  border: 'rgba(245,158,11,0.35)',   color: '#fbbf24', icon: '🌦️', label: 'Moderate' },
  'Low':      { bg: 'rgba(34,197,94,0.08)',   border: 'rgba(34,197,94,0.25)',    color: '#4ade80', icon: '☀️', label: 'Low Risk' },
};

function KPICard({ label, value, sub, icon, color }) {
  return (
    <div className="card" style={{
      padding: '1.5rem',
      border: `1px solid ${color}25`,
      background: `linear-gradient(135deg, ${color}0a 0%, rgba(22,32,25,0.9) 100%)`,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '-20px', right: '-10px',
        fontSize: '4rem', opacity: 0.07, userSelect: 'none',
        lineHeight: 1,
      }}>{icon}</div>
      <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.5rem' }}>
        {label}
      </div>
      <div style={{ fontSize: '2rem', fontWeight: 900, color, lineHeight: 1.1, marginBottom: '0.35rem' }}>
        {value}
      </div>
      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{sub}</div>
    </div>
  );
}

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
    <div style={{ overflow: 'hidden' }}>
      {/* ─── Page Hero ─── */}
      <section style={{
        position: 'relative',
        padding: '4rem 0 3rem',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'url(/agriculture.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center 20%',
          opacity: 0.06,
        }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse 70% 60% at 50% 0%, rgba(14,165,233,0.15) 0%, transparent 70%)',
        }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, transparent 60%, var(--bg-base) 100%)',
        }} />

        <div className="container" style={{ position: 'relative' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
            <span className="badge badge-sky">Module 3 · Time-Series ML</span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>34-Year IMD Climate Reanalysis · 30 Karnataka Districts</span>
          </div>
          <h1 style={{
            fontWeight: 900, marginBottom: '0.75rem',
            background: 'linear-gradient(135deg, #e8f5e9 0%, #38bdf8 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            District Agro-Weather Forecasting
          </h1>
          <p style={{ maxWidth: '680px', fontSize: '1.05rem', lineHeight: 1.6 }}>
            Multi-horizon rainfall probability and temperature predictions calibrated specifically for
            agricultural dry-spell identification and irrigation management.
          </p>
        </div>
      </section>

      {/* ─── Control Bar ─── */}
      <div className="container" style={{ marginBottom: '2rem' }}>
        <div className="card glass-card" style={{ padding: '1.5rem', border: '1px solid rgba(56,189,248,0.2)' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'flex-end' }}>
            <div style={{ minWidth: '220px', flex: 1 }}>
              <label className="form-label">📍 Karnataka District</label>
              <select
                className="form-select"
                value={district}
                onChange={e => setDistrict(e.target.value)}
                style={{ borderColor: 'rgba(56,189,248,0.3)' }}
              >
                {districts.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>

            <div>
              <label className="form-label">📅 Forecast Horizon</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {HORIZONS.map(h => (
                  <button
                    key={h}
                    onClick={() => setDays(h)}
                    style={{
                      padding: '0.5rem 1rem',
                      borderRadius: 'var(--radius-sm)',
                      border: days === h ? '1px solid #38bdf8' : '1px solid var(--border)',
                      background: days === h ? 'rgba(56,189,248,0.15)' : 'transparent',
                      color: days === h ? '#38bdf8' : 'var(--text-secondary)',
                      fontWeight: days === h ? 700 : 400,
                      fontSize: '0.88rem',
                      cursor: 'pointer',
                      transition: 'var(--transition)',
                    }}
                  >
                    +{h}d
                  </button>
                ))}
              </div>
            </div>

            <button
              className="btn"
              onClick={() => fetchWeather(district, days)}
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, rgba(14,165,233,0.8) 0%, rgba(22,163,74,0.8) 100%)',
                color: '#fff',
                border: 'none',
                padding: '0.65rem 1.5rem',
                boxShadow: '0 4px 20px rgba(14,165,233,0.3)',
              }}
            >
              {loading ? '⏳ Loading…' : '🔄 Refresh'}
            </button>
          </div>
        </div>
      </div>

      <div className="container" style={{ paddingBottom: '4rem' }}>
        {/* Loading */}
        {loading && (
          <div className="card glass-card" style={{ padding: '4rem', textAlign: 'center', border: '1px solid rgba(56,189,248,0.2)' }}>
            <div className="spinner" style={{ width: 48, height: 48, margin: '0 auto 1.25rem', borderWidth: 3, borderColor: 'rgba(56,189,248,0.2)', borderTopColor: '#38bdf8' }} />
            <p style={{ margin: 0, fontSize: '1rem', color: 'var(--text-secondary)' }}>
              Generating {days}-day meteorological forecast for <strong style={{ color: '#38bdf8' }}>{district}</strong>…
            </p>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="card" style={{ padding: '1.5rem', border: '1px solid rgba(239,68,68,0.35)', background: 'rgba(239,68,68,0.06)' }}>
            <div style={{ color: '#fca5a5', fontWeight: 700, marginBottom: '0.25rem' }}>⚠️ Failed to fetch weather forecast</div>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{error}</div>
          </div>
        )}

        {/* Forecast data */}
        {!loading && forecast && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

            {/* KPI Row */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1.25rem',
            }}>
              <KPICard
                label="Mean Rain Probability"
                value={`${summary.avg_rain_probability_pct ?? 0}%`}
                sub={`Averaged over next ${days} days`}
                icon="🌧️"
                color="#38bdf8"
              />
              <KPICard
                label="Total Expected Rainfall"
                value={`${summary.total_expected_rain_mm ?? 0} mm`}
                sub={`${summary.rainy_days_forecast ?? 0} rainy days forecast`}
                icon="💧"
                color="#60a5fa"
              />
              <KPICard
                label="Avg Max Temperature"
                value={summary.avg_temp_max_c ? `${summary.avg_temp_max_c}°C` : '—'}
                sub="Average daily high"
                icon="🌡️"
                color="#fbbf24"
              />
              <KPICard
                label="Irrigation Advisory"
                value={summary.irrigation_advisory?.split('—')[0]?.trim() || 'Monitor'}
                sub={summary.irrigation_advisory || 'Keep monitoring soil moisture.'}
                icon="🚿"
                color="#4ade80"
              />
            </div>

            {/* Daily grid */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <div style={{
                  width: 40, height: 40,
                  background: 'rgba(56,189,248,0.15)',
                  border: '1px solid rgba(56,189,248,0.3)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.2rem',
                }}>🌦️</div>
                <div>
                  <h2 style={{ margin: 0, fontSize: '1.3rem' }}>{district} · {days}-Day Outlook</h2>
                  <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    Starting {forecast.forecast_from}
                  </p>
                </div>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
                gap: '0.85rem',
              }}>
                {dayList.map((d, i) => {
                  const conf = RISK_CONFIG[d.rain_risk] || RISK_CONFIG['Low'];
                  const dateStr = new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
                  const weekday = new Date(d.date).toLocaleDateString('en-IN', { weekday: 'short' });
                  return (
                    <div
                      key={i}
                      className="card"
                      style={{
                        padding: '1rem 0.85rem',
                        textAlign: 'center',
                        background: conf.bg,
                        border: `1px solid ${conf.border}`,
                        cursor: 'default',
                        animation: 'fadeIn 0.4s ease forwards',
                        animationDelay: `${i * 0.02}s`,
                        opacity: 0,
                      }}
                    >
                      {/* Date */}
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
                        {weekday}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                        {dateStr}
                      </div>

                      {/* Icon */}
                      <div style={{ fontSize: '2rem', margin: '0.3rem 0' }}>{conf.icon}</div>

                      {/* Rain % */}
                      <div style={{ fontSize: '1.3rem', fontWeight: 900, color: conf.color, lineHeight: 1 }}>
                        {d.rain_probability_pct}%
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '0.6rem' }}>rain prob.</div>

                      {/* Divider */}
                      <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.5rem', marginBottom: '0.5rem' }}>
                        <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#60a5fa' }}>
                          {d.expected_rain_mm} mm
                        </div>
                        {d.temp_max_c && (
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                            {d.temp_min_c}° – {d.temp_max_c}°C
                          </div>
                        )}
                      </div>

                      {/* Badge */}
                      <span style={{
                        display: 'inline-block',
                        padding: '0.15rem 0.5rem',
                        background: conf.border,
                        color: conf.color,
                        borderRadius: '999px',
                        fontSize: '0.65rem',
                        fontWeight: 700,
                      }}>
                        {conf.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        )}

        {/* Empty state */}
        {!loading && !forecast && !error && (
          <div className="card glass-card" style={{ padding: '4rem', textAlign: 'center', border: '1px solid rgba(56,189,248,0.15)' }}>
            <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>🌦️</div>
            <h3 style={{ marginBottom: '0.5rem' }}>Select a District</h3>
            <p style={{ margin: 0 }}>Choose a Karnataka district above to load the AI weather forecast.</p>
          </div>
        )}
      </div>
    </div>
  );
}
