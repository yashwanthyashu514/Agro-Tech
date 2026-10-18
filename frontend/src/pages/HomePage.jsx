import React from 'react';
import { Navbar } from '../components/Navbar';

export function HomePage({ onNavigate }) {
  const features = [
    { icon: '📍', title: 'Location Intelligence', desc: 'Maps Karnataka taluks to agro-climatic zones and soil types automatically.' },
    { icon: '🌾', title: 'Crop Recommendation', desc: 'AI ranks 22 crops by suitability for your soil, season and climate with explained reasoning.' },
    { icon: '🌦️', title: 'Weather Forecasting', desc: '15-day district-level forecast with rain probability and irrigation advisories.' },
    { icon: '📅', title: 'Growth Stage Prediction', desc: 'GDD heat-unit model calculates exact germination to harvest dates for each crop.' },
    { icon: '📊', title: 'Yield Estimation', desc: 'XGBoost / LightGBM model predicts tonnes per hectare from soil, weather and history.' },
    { icon: '💡', title: 'AI Explanations', desc: 'Every recommendation shows why – which soil and weather values drove the decision.' },
  ];

  return (
    <div className="page-content">
      {/* Hero */}
      <section style={{ padding: '5rem 0 4rem', textAlign: 'center', position: 'relative' }}>
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse 60% 50% at 50% 0%, rgba(34,197,94,0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div className="container" style={{ position: 'relative' }}>
          <div style={{ marginBottom: '1rem' }}>
            <span className="badge badge-green" style={{ fontSize: '0.85rem', padding: '0.35rem 1rem' }}>
              Karnataka Agriculture Intelligence System
            </span>
          </div>
          <h1 style={{
            background: 'linear-gradient(135deg, #e8f5e9 0%, #4ade80 50%, #38bdf8 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            marginBottom: '1.25rem',
          }}>
            Grow Smarter,<br />Not by Chance
          </h1>
          <p style={{
            fontSize: '1.15rem', maxWidth: '600px', margin: '0 auto 2.5rem',
            color: 'var(--text-secondary)',
          }}>
            Enter your location and soil type. Our AI analyses weather patterns, 
            historical yields and crop biology to tell you exactly what to grow,
            when to grow it, and what to expect.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn btn-primary btn-lg" onClick={() => onNavigate('recommend')}>
              🌱 Get Started Free
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => onNavigate('about')}>
              How it Works
            </button>
          </div>
          {/* Stats */}
          <div className="grid-4" style={{ marginTop: '3.5rem', maxWidth: '700px', margin: '3.5rem auto 0' }}>
            {[
              { val: '22', label: 'Crops Supported' },
              { val: '30', label: 'Karnataka Districts' },
              { val: '34yr', label: 'Weather History' },
              { val: '99.5%', label: 'Model Accuracy' },
            ].map(({ val, label }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '2rem', fontWeight: 800,
                  background: 'var(--grad-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>{val}</div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '3rem 0' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <h2>Five AI Modules, One Platform</h2>
            <p style={{ maxWidth: '500px', margin: '0.75rem auto 0' }}>
              End-to-end decision support from soil to harvest.
            </p>
          </div>
          <div className="grid-3">
            {features.map(({ icon, title, desc }) => (
              <div key={title} className="card" style={{ cursor: 'default' }}>
                <div style={{
                  width: 52, height: 52,
                  background: 'rgba(34,197,94,0.12)',
                  border: '1px solid rgba(34,197,94,0.25)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.6rem', marginBottom: '1rem',
                }}>
                  {icon}
                </div>
                <h3 style={{ marginBottom: '0.5rem' }}>{title}</h3>
                <p style={{ fontSize: '0.88rem', margin: 0 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '3rem 0 2rem' }}>
        <div className="container">
          <div className="card glass-card" style={{
            textAlign: 'center', padding: '3rem 2rem',
            background: 'linear-gradient(135deg, rgba(22,163,74,0.08) 0%, rgba(14,165,233,0.08) 100%)',
          }}>
            <h2 style={{ marginBottom: '1rem' }}>Ready to know what to plant?</h2>
            <p style={{ maxWidth: '450px', margin: '0 auto 2rem' }}>
              Takes 30 seconds. Just pick your district and season — the AI does the rest.
            </p>
            <button className="btn btn-primary btn-lg" onClick={() => onNavigate('recommend')}>
              🌾 Analyse My Farm
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
