import React from 'react';

export function AboutPage() {
  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem 1.5rem 5rem' }}>
      
      {/* Header */}
      <div style={{ marginBottom: '3rem', textAlign: 'center' }}>
        <span className="badge badge-green" style={{ marginBottom: '0.8rem' }}>System Architecture & Engineering</span>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, margin: '0 0 1rem 0', letterSpacing: '-0.02em' }}>
          AgroTech Intelligence System
        </h1>
        <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', maxWidth: '650px', margin: '0 auto', lineHeight: 1.6 }}>
          An end-to-end AI decision-support platform designed to replace agricultural guesswork with rigorous 
          machine learning and climatological intelligence for Karnataka farmers.
        </p>
      </div>

      {/* 5 Core Modules Overview */}
      <div style={{ marginBottom: '3.5rem' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: '1.5rem' }}>The 5 Production AI Modules</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
          
          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>🗺️</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Module 1: Location & Soil Intelligence</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              Curated database covering 175 Karnataka taluks across 10 agro-climatic zones. Maps each taluk to dominant soil type,
              pH, Nitrogen (N), Phosphorus (P), Potassium (K), and organic carbon, with zone-level fallbacks.
            </p>
          </div>

          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>🌾</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Module 2: Crop Recommendation</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              Multinomial classifier trained across 22 major crops evaluated against soil chemistry and weather variables.
              Yields a calibrated suitability score with ICAR range-checking explainability.
            </p>
          </div>

          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>🌦️</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Module 3: Weather & Rainfall Forecasting</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              Time-series models trained on 380,000+ daily observations (1991–2025) across 30 Karnataka districts.
              Predicts rainfall probability, mm precipitation, and temperatures up to 90 days ahead with zero future leakage.
            </p>
          </div>

          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>📈</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Module 4: Phenological Growth Staging</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              Growing Degree Day (GDD) thermal accumulation model coupled with FAO-56 crop coefficients (Kc).
              Calculates exact calendar dates for germination, vegetative, flowering, and harvest, plus critical irrigation alerts.
            </p>
          </div>

          <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>⚖️</div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Module 5: Empirical Yield Prediction</h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              Ensemble regression model trained on 18,900+ Karnataka district historical yields (1998–2014) combined with 
              soil NPK, rainfall, and thermal profiles to output expected Tonnes/Hectare and confidence intervals.
            </p>
          </div>

        </div>
      </div>

      {/* Model Benchmark Specs */}
      <div style={{ marginBottom: '3.5rem' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: '1.5rem' }}>Empirical Model Evaluation</h2>
        <div className="card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Task</th>
                <th style={{ padding: '0.75rem 1rem' }}>Primary Algorithm</th>
                <th style={{ padding: '0.75rem 1rem' }}>Validation Metric</th>
                <th style={{ padding: '0.75rem 1rem' }}>Score</th>
                <th style={{ padding: '0.75rem 1rem' }}>Data Baseline</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Crop Suitability</td>
                <td style={{ padding: '0.75rem 1rem' }}>Random Forest (100 trees)</td>
                <td style={{ padding: '0.75rem 1rem' }}>Accuracy / Macro F1</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--green-400)', fontWeight: 700 }}>99.5% / 0.994</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>2,200 multi-soil records</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Yield Estimation</td>
                <td style={{ padding: '0.75rem 1rem' }}>LightGBM / XGBoost Regressor</td>
                <td style={{ padding: '0.75rem 1rem' }}>R² / RMSE</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--green-400)', fontWeight: 700 }}>R² = 0.94</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>18,957 Karnataka yields</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Rain Day Classification</td>
                <td style={{ padding: '0.75rem 1rem' }}>XGBoost Multi-Horizon Classifier</td>
                <td style={{ padding: '0.75rem 1rem' }}>ROC-AUC</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--green-400)', fontWeight: 700 }}>0.86 - 0.91</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>383,520 district-days</td>
              </tr>
              <tr>
                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Thermal Growth Stages</td>
                <td style={{ padding: '0.75rem 1rem' }}>GDD Thermal Accumulation</td>
                <td style={{ padding: '0.75rem 1rem' }}>Mean Stage Error</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--green-400)', fontWeight: 700 }}>± 3.2 days</td>
                <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>ICAR / FAO phenology standards</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Official Data Sources */}
      <div>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: '1.25rem' }}>Data Sources & References</h2>
        <div className="grid-2">
          <div className="card" style={{ padding: '1.25rem' }}>
            <h4 style={{ margin: '0 0 0.4rem 0', color: 'var(--green-400)' }}>Agricultural & Soil Databases</h4>
            <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.7 }}>
              <li>ICAR (Indian Council of Agricultural Research) agronomic handbooks</li>
              <li>ISRIC World Soil Information (SoilGrids 250m)</li>
              <li>Karnataka State Department of Agriculture (KSDA) taluk profiles</li>
              <li>Ministry of Agriculture & Farmers Welfare, Govt of India</li>
            </ul>
          </div>
          <div className="card" style={{ padding: '1.25rem' }}>
            <h4 style={{ margin: '0 0 0.4rem 0', color: 'var(--sky-400)' }}>Meteorological & Satellite Systems</h4>
            <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.7 }}>
              <li>India Meteorological Department (IMD) gridded rainfall data (1991–2025)</li>
              <li>NASA POWER Agroclimatology archive</li>
              <li>NOAA Global Surface Summary of the Day</li>
              <li>FAO-56 Irrigation and Drainage crop coefficient methodology</li>
            </ul>
          </div>
        </div>
      </div>

    </div>
  );
}
