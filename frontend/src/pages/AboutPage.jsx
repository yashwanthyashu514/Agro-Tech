import React from 'react';

const MODULE_COLORS = [
  { bg: 'rgba(74,222,128,0.12)', border: 'rgba(74,222,128,0.25)', glow: '#4ade80' },
  { bg: 'rgba(56,189,248,0.12)', border: 'rgba(56,189,248,0.25)', glow: '#38bdf8' },
  { bg: 'rgba(251,191,36,0.12)', border: 'rgba(251,191,36,0.25)', glow: '#fbbf24' },
  { bg: 'rgba(167,139,250,0.12)', border: 'rgba(167,139,250,0.25)', glow: '#a78bfa' },
  { bg: 'rgba(244,114,182,0.12)', border: 'rgba(244,114,182,0.25)', glow: '#f472b6' },
];

const modules = [
  {
    icon: '🗺️',
    num: '01',
    title: 'Location & Soil Intelligence',
    subtitle: 'Module 1',
    desc: 'Curated database covering 175 Karnataka taluks across 10 agro-climatic zones. Maps each taluk to dominant soil type, pH, Nitrogen (N), Phosphorus (P), Potassium (K), and organic carbon with zone-level fallbacks.',
    tags: ['175 Taluks', '10 Agro Zones', 'NPK Profiles', 'Auto-mapping'],
  },
  {
    icon: '🌾',
    num: '02',
    title: 'Crop Recommendation',
    subtitle: 'Module 2',
    desc: 'Multinomial classifier trained on 22 major Karnataka crops evaluated against soil chemistry, season and weather variables. Yields a calibrated suitability score with ICAR range-checking explainability.',
    tags: ['22 Crops', 'Random Forest', '99.5% Accuracy', 'ICAR Ranges'],
  },
  {
    icon: '🌦️',
    num: '03',
    title: 'Weather & Rainfall Forecasting',
    subtitle: 'Module 3',
    desc: 'Time-series models trained on 383,520 daily observations (1991–2025) across 30 Karnataka districts. Predicts rainfall probability, mm precipitation and temperatures up to 90 days ahead with zero future leakage.',
    tags: ['383K+ Records', '30 Districts', '90-day Horizon', 'XGBoost'],
  },
  {
    icon: '📈',
    num: '04',
    title: 'Phenological Growth Staging',
    subtitle: 'Module 4',
    desc: 'Growing Degree Day (GDD) thermal accumulation model coupled with FAO-56 crop coefficients (Kc). Calculates exact calendar dates for germination, vegetative, flowering and harvest, plus critical irrigation alerts.',
    tags: ['GDD Model', 'FAO-56 Kc', '±3.2 Day Error', 'BBCH Stages'],
  },
  {
    icon: '⚖️',
    num: '05',
    title: 'Empirical Yield Prediction',
    subtitle: 'Module 5',
    desc: 'Ensemble regression trained on 18,957 Karnataka district historical yields (1998–2014) combined with soil NPK, rainfall and thermal profiles. Outputs expected Tonnes/Hectare with confidence intervals.',
    tags: ['18,957 Records', 'LightGBM', 'R² = 0.94', 'Tonnes/Ha'],
  },
];

const benchmarks = [
  { task: 'Crop Suitability', algo: 'Random Forest (100 trees)', metric: 'Accuracy / Macro F1', score: '99.5% / 0.994', data: '2,200 multi-soil records' },
  { task: 'Yield Estimation', algo: 'LightGBM / XGBoost Regressor', metric: 'R² / RMSE', score: 'R² = 0.94', data: '18,957 Karnataka yields' },
  { task: 'Rain Day Classification', algo: 'XGBoost Multi-Horizon', metric: 'ROC-AUC', score: '0.86 – 0.91', data: '383,520 district-days' },
  { task: 'Thermal Growth Stages', algo: 'GDD Thermal Accumulation', metric: 'Mean Stage Error', score: '± 3.2 days', data: 'ICAR / FAO phenology' },
];

export function AboutPage() {
  return (
    <div style={{ overflow: 'hidden' }}>
      {/* ─── Hero Banner ─── */}
      <section style={{
        position: 'relative',
        padding: '5rem 0 4rem',
        overflow: 'hidden',
      }}>
        {/* Faded agriculture background */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'url(/agriculture.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center 30%',
          opacity: 0.07,
        }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, transparent 0%, var(--bg-base) 100%)',
        }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(22,163,74,0.15) 0%, transparent 70%)',
        }} />

        <div className="container" style={{ position: 'relative', textAlign: 'center' }}>
          <span className="badge badge-green" style={{ marginBottom: '1.25rem', fontSize: '0.82rem' }}>
            System Architecture & Engineering
          </span>
          <h1 style={{
            fontWeight: 900,
            marginBottom: '1.25rem',
            background: 'linear-gradient(135deg, #e8f5e9 0%, #4ade80 50%, #38bdf8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            AgroTech Intelligence System
          </h1>
          <p style={{ fontSize: '1.1rem', maxWidth: '680px', margin: '0 auto', lineHeight: 1.7 }}>
            An end-to-end AI decision-support platform replacing agricultural guesswork with rigorous
            machine learning and climatological intelligence for Karnataka farmers.
          </p>

          {/* Quick stats */}
          <div style={{
            display: 'flex', flexWrap: 'wrap', justifyContent: 'center',
            gap: '1.5rem', marginTop: '3rem',
          }}>
            {[
              { val: '5', label: 'AI Modules' },
              { val: '175', label: 'Taluks Mapped' },
              { val: '383K+', label: 'Weather Records' },
              { val: '18,957', label: 'Yield Records' },
              { val: '22', label: 'Crops Supported' },
            ].map(({ val, label }) => (
              <div key={label} style={{
                padding: '1rem 1.5rem',
                background: 'rgba(22,163,74,0.06)',
                border: '1px solid rgba(74,222,128,0.2)',
                borderRadius: 'var(--radius-md)',
                textAlign: 'center',
                backdropFilter: 'blur(8px)',
              }}>
                <div style={{
                  fontSize: '1.7rem', fontWeight: 900,
                  background: 'linear-gradient(135deg, #4ade80 0%, #38bdf8 100%)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>{val}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── 5 Modules ─── */}
      <section style={{ padding: '4rem 0' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>Technical Architecture</span>
            <h2 style={{ fontWeight: 900 }}>The 5 Production AI Modules</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {modules.map(({ icon, num, title, subtitle, desc, tags }, i) => {
              const c = MODULE_COLORS[i];
              return (
                <div
                  key={num}
                  className="card"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '80px 1fr',
                    gap: '1.5rem',
                    alignItems: 'start',
                    border: `1px solid ${c.border}`,
                    background: `linear-gradient(135deg, ${c.bg} 0%, rgba(22,32,25,0.8) 100%)`,
                    transition: 'var(--transition)',
                  }}
                >
                  {/* Left: icon + number */}
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: 56, height: 56,
                      background: `${c.bg}`,
                      border: `1px solid ${c.border}`,
                      borderRadius: 'var(--radius-md)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '1.8rem', margin: '0 auto 0.5rem',
                      boxShadow: `0 0 24px ${c.glow}20`,
                    }}>
                      {icon}
                    </div>
                    <div style={{
                      fontSize: '0.7rem', fontWeight: 700,
                      color: c.glow, letterSpacing: '0.1em',
                    }}>
                      {num}
                    </div>
                  </div>

                  {/* Right: content */}
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.3rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                      {subtitle}
                    </div>
                    <h3 style={{ fontSize: '1.2rem', marginBottom: '0.6rem', color: '#e8f5e9' }}>{title}</h3>
                    <p style={{ fontSize: '0.9rem', margin: '0 0 1rem', lineHeight: 1.65 }}>{desc}</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {tags.map(t => (
                        <span key={t} style={{
                          padding: '0.2rem 0.7rem',
                          background: `${c.glow}18`,
                          border: `1px solid ${c.glow}35`,
                          borderRadius: '999px',
                          fontSize: '0.75rem',
                          color: c.glow,
                          fontWeight: 600,
                        }}>{t}</span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─── Model Benchmarks ─── */}
      <section style={{
        padding: '4rem 0',
        background: 'linear-gradient(135deg, rgba(22,163,74,0.04) 0%, rgba(14,165,233,0.04) 100%)',
        borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)',
      }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <span className="badge badge-sky" style={{ marginBottom: '0.75rem' }}>Validated Performance</span>
            <h2 style={{ fontWeight: 900 }}>Empirical Model Evaluation</h2>
          </div>

          <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(22,163,74,0.08)' }}>
                    {['Task', 'Algorithm', 'Metric', 'Score', 'Dataset'].map(h => (
                      <th key={h} style={{ padding: '1rem 1.25rem', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap' }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {benchmarks.map(({ task, algo, metric, score, data }, i) => (
                    <tr key={task} style={{ borderBottom: i < benchmarks.length - 1 ? '1px solid var(--border)' : 'none', transition: 'var(--transition)' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(34,197,94,0.04)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                      <td style={{ padding: '1rem 1.25rem', fontWeight: 700, color: '#e8f5e9' }}>{task}</td>
                      <td style={{ padding: '1rem 1.25rem', color: 'var(--text-secondary)', fontSize: '0.87rem' }}>{algo}</td>
                      <td style={{ padding: '1rem 1.25rem', color: 'var(--text-secondary)', fontSize: '0.87rem' }}>{metric}</td>
                      <td style={{ padding: '1rem 1.25rem' }}>
                        <span style={{
                          color: 'var(--green-400)', fontWeight: 800, fontSize: '0.95rem',
                          background: 'rgba(74,222,128,0.1)',
                          padding: '0.2rem 0.6rem',
                          borderRadius: '6px',
                          border: '1px solid rgba(74,222,128,0.2)',
                        }}>{score}</span>
                      </td>
                      <td style={{ padding: '1rem 1.25rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>{data}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Data Sources ─── */}
      <section style={{ padding: '4rem 0 5rem' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>Verified Data</span>
            <h2 style={{ fontWeight: 900 }}>Data Sources & References</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            {[
              {
                icon: '🌱',
                title: 'Agricultural & Soil Databases',
                color: '#4ade80',
                items: [
                  'ICAR agronomic handbooks & crop calendars',
                  'ISRIC World Soil Information (SoilGrids 250m)',
                  'Karnataka State Dept. of Agriculture (KSDA)',
                  'Ministry of Agriculture & Farmers Welfare',
                ],
              },
              {
                icon: '🌦️',
                title: 'Meteorological & Satellite Data',
                color: '#38bdf8',
                items: [
                  'India Meteorological Department (IMD) 1991–2025',
                  'NASA POWER Agroclimatology archive',
                  'NOAA Global Surface Summary of the Day',
                  'FAO-56 Irrigation & Drainage methodology',
                ],
              },
              {
                icon: '📊',
                title: 'Yield & Production Records',
                color: '#fbbf24',
                items: [
                  'Karnataka Directorate of Economics & Statistics',
                  'GoI – District-wise area and production 1998–2014',
                  'APEDA commodity export records',
                  'APMC mandi price archives',
                ],
              },
            ].map(({ icon, title, color, items }) => (
              <div key={title} className="card" style={{
                border: `1px solid ${color}25`,
                background: `linear-gradient(135deg, ${color}08 0%, rgba(22,32,25,0.8) 100%)`,
              }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem',
                  marginBottom: '1rem', paddingBottom: '0.75rem',
                  borderBottom: '1px solid var(--border)',
                }}>
                  <span style={{ fontSize: '1.4rem' }}>{icon}</span>
                  <h4 style={{ margin: 0, color, fontSize: '0.95rem' }}>{title}</h4>
                </div>
                <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-secondary)', fontSize: '0.87rem', lineHeight: 1.8 }}>
                  {items.map(item => <li key={item}>{item}</li>)}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
