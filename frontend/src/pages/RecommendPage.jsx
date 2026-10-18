import React from 'react';
import { RecommendForm } from '../components/RecommendForm';
import { CropResults } from '../components/CropResults';
import { useRecommend } from '../hooks/useAgrotech';

const PRESETS = [
  { district: 'Davanagere', taluk: 'Davanagere', season: 'Kharif', desc: 'Central Dry Zone · Black/Red Soil' },
  { district: 'Shimoga', taluk: 'Shimoga', season: 'Kharif', desc: 'Southern Transition · High Rainfall' },
  { district: 'Dharwad', taluk: 'Dharwad', season: 'Rabi', desc: 'Northern Transition · Deep Black Soil' },
  { district: 'Mysore', taluk: 'Mysore', season: 'Kharif', desc: 'Southern Dry Zone · Red Loam' },
];

export function RecommendPage() {
  const { data, loading, error, submit } = useRecommend();

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1.5rem 4rem' }}>
      
      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.4rem' }}>
          <span className="badge badge-green">AI Advisory Engine</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Karnataka State Coverage (30 Districts)</span>
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, margin: '0 0 0.5rem 0', letterSpacing: '-0.02em' }}>
          Smart Crop Recommendation & Growth Planner
        </h1>
        <p style={{ margin: 0, fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', lineHeight: 1.5 }}>
          Enter your location and season. AgroTech automatically infers taluk-level soil chemistry, 34-year rainfall patterns, 
          forecasts 15-day weather, and predicts crop suitability, growth stages, and yield.
        </p>
      </div>

      {/* Main Grid: Form + Results */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2.5rem' }}>
        
        {/* Form Container */}
        <div>
          <RecommendForm onSubmit={submit} loading={loading} />
        </div>

        {/* Status / Output Section */}
        <div>
          {loading && (
            <div className="card glass-card" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
              <div className="spinner" style={{ width: 44, height: 44, margin: '0 auto 1.5rem', borderWidth: 3 }}></div>
              <h3 style={{ margin: '0 0 0.5rem 0', fontWeight: 700 }}>Synthesizing Agricultural Intelligence…</h3>
              <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
                Querying ISRIC SoilGrids, IMD climate history, running XGBoost/Random Forest models & generating growth timeline…
              </p>
            </div>
          )}

          {error && (
            <div className="card" style={{
              padding: '1.5rem',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              background: 'rgba(239, 68, 68, 0.08)',
              marginBottom: '1.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '1.5rem' }}>⚠️</span>
                <div>
                  <h4 style={{ margin: '0 0 0.25rem 0', color: '#fca5a5' }}>Recommendation Request Failed</h4>
                  <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{error}</p>
                </div>
              </div>
            </div>
          )}

          {!loading && !data && !error && (
            <div className="card glass-card" style={{ padding: '2.5rem 2rem' }}>
              <div style={{ textAlign: 'center', maxWidth: '540px', margin: '0 auto 2rem' }}>
                <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🌱</div>
                <h3 style={{ margin: '0 0 0.5rem 0', fontWeight: 700 }}>Ready to Generate Recommendations</h3>
                <p style={{ margin: 0, fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  Select your district and taluk on the form above, or click one of the pre-configured Karnataka agro-climatic scenarios below to test instantly:
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
                {PRESETS.map((p, idx) => (
                  <div
                    key={idx}
                    className="card interactive-card"
                    onClick={() => submit({ district: p.district, taluk: p.taluk, season: p.season, top_n: 5 })}
                    style={{
                      padding: '1.25rem',
                      cursor: 'pointer',
                      border: '1px solid var(--border)',
                      transition: 'all 0.2s ease',
                      background: 'rgba(255, 255, 255, 0.02)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <span style={{ fontWeight: 700, color: 'var(--green-400)' }}>{p.district}</span>
                      <span className="badge badge-sky" style={{ fontSize: '0.7rem' }}>{p.season}</span>
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                      Taluk: {p.taluk}
                    </div>
                    <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      {p.desc}
                    </div>
                    <div style={{ marginTop: '0.75rem', fontSize: '0.78rem', color: 'var(--green-500)', fontWeight: 600 }}>
                      Run Demo →
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {data && <CropResults data={data} />}
        </div>

      </div>
    </div>
  );
}
