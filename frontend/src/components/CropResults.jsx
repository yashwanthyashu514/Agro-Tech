import React, { useState } from 'react';

const CROP_EMOJIS = {
  rice: '🌾', maize: '🌽', chickpea: '🫘', pigeonpeas: '🫘',
  mungbean: '🌿', blackgram: '🫘', lentil: '🫘', mothbeans: '🫘',
  kidneybeans: '🫘', cotton: '🌸', jute: '🌿', banana: '🍌',
  mango: '🥭', grapes: '🍇', watermelon: '🍉', muskmelon: '🍈',
  papaya: '🍈', pomegranate: '🍎', coffee: '☕', coconut: '🥥',
  orange: '🍊', apple: '🍎',
};

function SuitabilityBar({ score }) {
  const pct = Math.round(score * 100);
  const color = pct >= 70 ? 'var(--green-500)' : pct >= 40 ? 'var(--amber-500)' : '#ef4444';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div className="progress-bar" style={{ flex: 1 }}>
        <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span style={{ minWidth: '3rem', color, fontWeight: 700, fontSize: '1.05rem' }}>{pct}%</span>
    </div>
  );
}

function ReasonList({ reasons }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.75rem' }}>
      {reasons.map((r, i) => (
        <div key={i} style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          fontSize: '0.82rem', color: r.status === 'OK' ? 'var(--text-secondary)' : '#fca5a5',
          padding: '0.3rem 0.5rem',
          borderRadius: 'var(--radius-sm)',
          background: r.status === 'OK' ? 'rgba(34,197,94,0.05)' : 'rgba(239,68,68,0.08)',
        }}>
          <span>{r.status === 'OK' ? '✓' : '⚠'}</span>
          <span style={{ flex: 1 }}><strong>{r.feature}</strong>: {r.value}</span>
          <span style={{ opacity: 0.7 }}>Typical: {r.typical_range}</span>
        </div>
      ))}
    </div>
  );
}

function CropCard({ rec, rank, isTop, defaultExpanded }) {
  const [expanded, setExpanded] = useState(defaultExpanded || false);
  const emoji = CROP_EMOJIS[rec.crop] || '🌱';
  const pct = Math.round(rec.suitability_score * 100);

  return (
    <div className="card fade-in" style={{
      border: isTop ? '1px solid rgba(34,197,94,0.4)' : undefined,
      boxShadow: isTop ? '0 0 30px rgba(34,197,94,0.12)' : undefined,
    }}>
      {/* header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{
          width: 52, height: 52, borderRadius: 'var(--radius-md)',
          background: isTop ? 'rgba(34,197,94,0.15)' : 'rgba(255,255,255,0.04)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.7rem', flexShrink: 0,
          border: isTop ? '1px solid rgba(34,197,94,0.3)' : '1px solid var(--border)',
        }}>
          {emoji}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0, textTransform: 'capitalize' }}>
              #{rank} {rec.crop}
            </h3>
            {isTop && <span className="badge badge-green">Top Pick</span>}
            <span className="badge badge-blue">{rec.season}</span>
          </div>
          {rec.duration_days && (
            <p style={{ margin: '0.2rem 0 0', fontSize: '0.83rem' }}>
              Duration: ~{rec.duration_days} days
              {rec.water_requirement && ` · ${rec.water_requirement}`}
            </p>
          )}
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.35rem' }}>
            {rec.profit_estimate && (
              <span className="badge badge-green" style={{ fontSize: '0.72rem', padding: '0.15rem 0.5rem' }}>
                💰 {rec.profit_estimate}
              </span>
            )}
            {rec.ease_of_growth && (
              <span className="badge badge-sky" style={{ fontSize: '0.72rem', padding: '0.15rem 0.5rem' }}>
                🌱 {rec.ease_of_growth.split('(')[0].trim()}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={() => setExpanded(e => !e)}
          className="btn btn-secondary"
          style={{ padding: '0.4rem 0.8rem', fontSize: '0.82rem' }}>
          {expanded ? 'Less' : 'Details'}
        </button>
      </div>

      <SuitabilityBar score={rec.suitability_score} />

      {/* Multi-Criteria Intelligence: Soil, Ease, Market */}
      <div style={{
        marginTop: '0.75rem',
        padding: '0.65rem 0.85rem',
        background: 'rgba(255, 255, 255, 0.02)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.35rem',
        fontSize: '0.82rem',
      }}>
        {rec.soil_suitability && (
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
            <span>🌍</span>
            <span style={{ color: 'var(--text-secondary)' }}><strong>Soil Match:</strong> {rec.soil_suitability}</span>
          </div>
        )}
        {rec.ease_of_growth && (
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
            <span>🛠️</span>
            <span style={{ color: 'var(--text-secondary)' }}><strong>Cultivation:</strong> {rec.ease_of_growth}</span>
          </div>
        )}
        {rec.market_demand && (
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
            <span>📈</span>
            <span style={{ color: 'var(--text-secondary)' }}><strong>Mandi & Returns:</strong> {rec.market_demand}</span>
          </div>
        )}
      </div>

      {/* Temp & Rain range */}
      {(rec.min_temp_c || rec.min_rainfall_mm) && (
        <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
          {rec.min_temp_c && (
            <span className="tag">🌡 {rec.min_temp_c}°–{rec.max_temp_c}°C</span>
          )}
          {rec.min_rainfall_mm && (
            <span className="tag">🌧 {rec.min_rainfall_mm}–{rec.max_rainfall_mm} mm/yr</span>
          )}
        </div>
      )}

      {/* Yield */}
      {rec.yield_prediction && (
        <div style={{
          marginTop: '0.75rem', padding: '0.75rem 1rem',
          background: 'rgba(34,197,94,0.06)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid rgba(34,197,94,0.15)',
          display: 'flex', gap: '1.5rem', flexWrap: 'wrap',
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
              Predicted Yield
            </div>
            <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--green-400)' }}>
              {rec.yield_prediction.predicted_t_ha} t/ha
            </div>
          </div>
          {rec.yield_prediction.district_avg_3yr_t_ha && (
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
                District 3-yr Avg
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                {rec.yield_prediction.district_avg_3yr_t_ha} t/ha
              </div>
            </div>
          )}
          {rec.yield_prediction.based_on_year && (
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>
                Data up to
              </div>
              <div style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>
                {rec.yield_prediction.based_on_year}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Expanded: reasons */}
      {expanded && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)',
            marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Why this crop?
          </div>
          <ReasonList reasons={rec.reasons} />
        </div>
      )}
    </div>
  );
}

export function CropResults({ data }) {
  if (!data) return null;
  const { location, season, soil, weather, recommendations, growth_plan, weather_forecast, model_info } = data;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

      {/* Summary bar */}
      <div className="card glass-card" style={{ padding: '1.25rem 1.5rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Location</div>
            <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>{location.taluk}, {location.district}</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{location.agro_zone}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Soil</div>
            <div style={{ fontWeight: 600 }}>{location.dominant_soil}</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              N:{soil.N} · P:{soil.P} · K:{soil.K} · pH:{soil.ph}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Weather ({season})</div>
            <div style={{ fontWeight: 600 }}>🌡 {weather.temperature}°C · 💧 {weather.humidity}% · 🌧 {weather.rainfall} mm/mo</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{weather.source}</div>
          </div>
          <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Model</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--green-400)' }}>{model_info.crop_model}</div>
          </div>
        </div>
      </div>

      {/* Crop recommendations */}
      <div>
        <div className="section-title">
          <div className="icon">🌾</div>
          <div>
            <h2 style={{ margin: 0 }}>Crop Recommendations</h2>
            <p style={{ margin: 0, fontSize: '0.85rem' }}>Ranked by AI suitability score for your conditions</p>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {recommendations.map((rec, i) => (
            <CropCard key={rec.crop} rec={rec} rank={i + 1} isTop={i === 0} defaultExpanded={i === 0} />
          ))}
        </div>
      </div>

      {/* Growth Plan */}
      {growth_plan && growth_plan.stages.length > 0 && (
        <GrowthPlanSection plan={growth_plan} />
      )}

      {/* Weather Forecast */}
      {weather_forecast && weather_forecast.days.length > 0 && (
        <WeatherForecastSection forecast={weather_forecast} />
      )}
    </div>
  );
}

function GrowthPlanSection({ plan }) {
  const totalDays = plan.total_duration_days;
  return (
    <div>
      <div className="section-title">
        <div className="icon">📅</div>
        <div>
          <h2 style={{ margin: 0 }}>Growth Timeline – {plan.crop}</h2>
          <p style={{ margin: 0, fontSize: '0.85rem' }}>
            Sown {plan.sow_date} · {plan.prediction_type}
            {totalDays ? ` · ~${totalDays} days total` : ''}
          </p>
        </div>
      </div>
      <div className="card">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {plan.stages.map((stage, i) => (
            <StageRow key={i} stage={stage} isLast={i === plan.stages.length - 1} />
          ))}
        </div>
      </div>
    </div>
  );
}

function StageRow({ stage, isLast }) {
  const water_colors = {
    'Low': 'var(--sky-400)', 'Medium': 'var(--amber-400)',
    'High': '#f87171', 'Very Low': '#a7c4a3', 'Stop irrigation': 'var(--text-muted)',
  };
  const wc = Object.entries(water_colors).find(([k]) => stage.water_need?.includes(k))?.[1] || 'var(--text-secondary)';
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: '1rem',
      paddingBottom: isLast ? 0 : '1.25rem',
      borderBottom: isLast ? 'none' : '1px solid var(--border)',
      marginBottom: isLast ? 0 : '1.25rem',
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
        <div style={{
          width: 12, height: 12, borderRadius: '50%',
          background: 'var(--green-500)', border: '2px solid var(--green-700)',
          marginTop: '0.3rem',
        }} />
        {!isLast && <div style={{ width: 2, flex: 1, background: 'var(--border)', marginTop: '4px' }} />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
          <strong style={{ fontSize: '0.95rem' }}>{stage.stage}</strong>
          {stage.critical_irrigation === 'Yes' && (
            <span className="badge badge-blue">Critical Irrigation</span>
          )}
          {stage.water_need && (
            <span style={{ fontSize: '0.8rem', color: wc, fontWeight: 500 }}>
              💧 {stage.water_need}
            </span>
          )}
        </div>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          {stage.start_date} → {stage.end_date || 'TBD'}
          {stage.days_after_sowing && ` · DAS ${stage.days_after_sowing}`}
          {stage.kc && ` · Kc=${stage.kc}`}
        </div>
      </div>
    </div>
  );
}

function WeatherForecastSection({ forecast }) {
  const { summary, days } = forecast;
  const risk_colors = { Low: 'var(--green-400)', Moderate: 'var(--amber-400)', High: '#f87171' };
  return (
    <div>
      <div className="section-title">
        <div className="icon">🌦️</div>
        <div>
          <h2 style={{ margin: 0 }}>15-Day Weather Forecast</h2>
          <p style={{ margin: 0, fontSize: '0.85rem' }}>{forecast.district} · from {forecast.forecast_from}</p>
        </div>
      </div>
      {/* Summary */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Avg Rain Probability</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--sky-400)' }}>{summary.avg_rain_probability_pct}%</div>
        </div>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Expected Rain</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--sky-400)' }}>{summary.total_expected_rain_mm} mm</div>
        </div>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Irrigation Advisory</div>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)', marginTop: '0.25rem', lineHeight: 1.5 }}>{summary.irrigation_advisory}</div>
        </div>
      </div>
      {/* Day cards */}
      <div style={{ overflowX: 'auto' }}>
        <div style={{ display: 'flex', gap: '0.7rem', paddingBottom: '0.5rem', minWidth: 'max-content' }}>
          {days.map((day, i) => (
            <div key={i} className="card" style={{
              padding: '0.9rem', minWidth: '110px', textAlign: 'center',
              border: day.rain_risk === 'High' ? '1px solid rgba(248,113,113,0.3)' : undefined,
            }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>
                {new Date(day.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
              </div>
              <div style={{ fontSize: '1.6rem', margin: '0.3rem 0' }}>
                {day.rain_probability_pct >= 65 ? '🌧' : day.rain_probability_pct >= 35 ? '🌤' : '☀️'}
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: risk_colors[day.rain_risk] }}>
                {day.rain_probability_pct}%
              </div>
              {day.temp_max_c && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  {day.temp_min_c}°–{day.temp_max_c}°C
                </div>
              )}
              <div style={{ fontSize: '0.72rem', color: 'var(--sky-400)', marginTop: '0.2rem' }}>
                {day.expected_rain_mm} mm
              </div>
              <div style={{
                fontSize: '0.65rem', marginTop: '0.3rem',
                color: risk_colors[day.rain_risk], fontWeight: 600,
              }}>
                {day.rain_risk}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
