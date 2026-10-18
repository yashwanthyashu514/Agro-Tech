import React, { useEffect, useRef } from 'react';

export function HomePage({ onNavigate }) {
  const heroRef = useRef(null);

  // Parallax effect on hero image
  useEffect(() => {
    const handleScroll = () => {
      if (heroRef.current) {
        heroRef.current.style.transform = `translateY(${window.scrollY * 0.35}px)`;
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      icon: '📍',
      title: 'Location Intelligence',
      desc: 'Maps all 175 Karnataka taluks to agro-climatic zones, soil types, pH, NPK and organic carbon automatically.',
      color: '#4ade80',
    },
    {
      icon: '🌾',
      title: 'Crop Recommendation',
      desc: 'AI ranks 22 crops by suitability for your soil, season and climate — with full explainability.',
      color: '#38bdf8',
    },
    {
      icon: '🌦️',
      title: 'Weather Forecasting',
      desc: '15-day district forecast with rain probability, mm estimates and irrigation advisories.',
      color: '#fbbf24',
    },
    {
      icon: '📅',
      title: 'Growth Stage Prediction',
      desc: 'GDD heat-unit model calculates exact germination-to-harvest dates for every recommended crop.',
      color: '#a78bfa',
    },
    {
      icon: '📊',
      title: 'Yield Estimation',
      desc: 'LightGBM / XGBoost predicts tonnes per hectare from soil chemistry, rainfall and 18 k historical records.',
      color: '#f472b6',
    },
    {
      icon: '💡',
      title: 'AI Explanations',
      desc: 'Every recommendation shows exactly which soil and weather values drove the decision.',
      color: '#34d399',
    },
  ];

  const stats = [
    { val: '22', label: 'Crops', sub: 'Supported' },
    { val: '30', label: 'Districts', sub: 'Karnataka' },
    { val: '34yr', label: 'Weather', sub: 'History' },
    { val: '99.5%', label: 'Accuracy', sub: 'Model Score' },
  ];

  return (
    <div style={{ overflow: 'hidden' }}>
      {/* ═══ HERO ═══ */}
      <section style={{ position: 'relative', height: '100vh', minHeight: '650px', display: 'flex', alignItems: 'center', overflow: 'hidden' }}>
        {/* Parallax background */}
        <div
          ref={heroRef}
          style={{
            position: 'absolute',
            inset: '-15% 0',
            backgroundImage: 'url(/agriculture.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center 40%',
            filter: 'brightness(0.35) saturate(1.2)',
            willChange: 'transform',
          }}
        />

        {/* Overlays */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(10,15,13,0.3) 0%, rgba(10,15,13,0.5) 50%, rgba(10,15,13,0.98) 100%)',
        }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse 60% 70% at 30% 40%, rgba(22,163,74,0.18) 0%, transparent 65%)',
        }} />

        {/* Floating particles */}
        {[...Array(6)].map((_, i) => (
          <div key={i} style={{
            position: 'absolute',
            width: `${[6,4,8,5,7,4][i]}px`,
            height: `${[6,4,8,5,7,4][i]}px`,
            borderRadius: '50%',
            background: `rgba(74,222,128,${[0.6,0.4,0.5,0.7,0.3,0.5][i]})`,
            left: `${[15,72,88,8,55,40][i]}%`,
            top: `${[25,40,65,70,20,55][i]}%`,
            animation: `float-particle ${[4,5,6,4.5,5.5,6.5][i]}s ease-in-out infinite`,
            animationDelay: `${[0,1,2,0.5,1.5,2.5][i]}s`,
            boxShadow: '0 0 10px rgba(74,222,128,0.5)',
          }} />
        ))}

        <div className="container" style={{ position: 'relative', zIndex: 2 }}>
          <div style={{ maxWidth: '720px' }}>
            <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <span className="badge badge-green" style={{ fontSize: '0.8rem', padding: '0.4rem 1rem', backdropFilter: 'blur(8px)' }}>
                🌱 Karnataka Agriculture AI
              </span>
              <span className="badge badge-sky" style={{ fontSize: '0.8rem', padding: '0.4rem 1rem', backdropFilter: 'blur(8px)' }}>
                5 AI Modules
              </span>
            </div>

            <h1 style={{
              fontSize: 'clamp(2.4rem, 6vw, 4rem)',
              fontWeight: 900,
              lineHeight: 1.1,
              marginBottom: '1.5rem',
              letterSpacing: '-0.03em',
            }}>
              <span style={{
                background: 'linear-gradient(135deg, #ffffff 0%, #e8f5e9 40%, #4ade80 70%, #38bdf8 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                Grow Smarter,
              </span>
              <br />
              <span style={{ color: '#e8f5e9' }}>Not by Chance</span>
            </h1>

            <p style={{
              fontSize: 'clamp(1rem, 2vw, 1.2rem)',
              color: 'rgba(232,245,233,0.8)',
              lineHeight: 1.7,
              marginBottom: '2.5rem',
              maxWidth: '580px',
            }}>
              Enter your location and season. Our AI analyses 34 years of weather, 
              soil chemistry and 18,000+ yield records to tell you exactly what to grow,
              when to grow it, and what to expect at harvest.
            </p>

            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '3.5rem' }}>
              <button
                className="btn btn-primary btn-lg"
                onClick={() => onNavigate('recommend')}
                style={{
                  background: 'linear-gradient(135deg, #16a34a 0%, #0ea5e9 100%)',
                  boxShadow: '0 8px 32px rgba(22,163,74,0.45), 0 0 0 1px rgba(74,222,128,0.2)',
                  fontSize: '1.05rem',
                  padding: '1rem 2.2rem',
                }}
              >
                🌱 Analyse My Farm — Free
              </button>
              <button
                className="btn btn-secondary btn-lg"
                onClick={() => onNavigate('weather')}
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  backdropFilter: 'blur(12px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  color: '#e8f5e9',
                }}
              >
                🌦️ Check Weather Forecast
              </button>
            </div>

            {/* Stats Row */}
            <div style={{ display: 'flex', gap: '2.5rem', flexWrap: 'wrap' }}>
              {stats.map(({ val, label, sub }) => (
                <div key={label}>
                  <div style={{
                    fontSize: 'clamp(1.8rem,4vw,2.4rem)',
                    fontWeight: 900,
                    background: 'linear-gradient(135deg, #4ade80 0%, #38bdf8 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    lineHeight: 1,
                  }}>{val}</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#e8f5e9', marginTop: '0.2rem' }}>{label}</div>
                  <div style={{ fontSize: '0.75rem', color: 'rgba(167,196,163,0.7)' }}>{sub}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div style={{
          position: 'absolute', bottom: '2.5rem', left: '50%', transform: 'translateX(-50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem',
          color: 'rgba(255,255,255,0.4)', fontSize: '0.75rem', letterSpacing: '0.1em',
          animation: 'bounce-down 2s ease-in-out infinite',
        }}>
          <span>SCROLL</span>
          <svg width="16" height="20" viewBox="0 0 16 20" fill="none">
            <path d="M8 0v16M1 9l7 7 7-7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </section>

      {/* ═══ FEATURES ═══ */}
      <section style={{ padding: '6rem 0', position: 'relative', background: 'var(--bg-base)' }}>
        {/* Top gradient fade from hero */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: '120px',
          background: 'linear-gradient(to bottom, rgba(10,15,13,0.98) 0%, transparent 100%)',
          pointerEvents: 'none',
        }} />

        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <span className="badge badge-green" style={{ marginBottom: '1rem' }}>Platform Capabilities</span>
            <h2 style={{
              fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
              fontWeight: 900,
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #e8f5e9 0%, #4ade80 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Five AI Modules, One Platform
            </h2>
            <p style={{ maxWidth: '500px', margin: '0 auto', fontSize: '1.05rem' }}>
              End-to-end decision support — from soil analysis to harvest yield estimation.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '1.5rem',
          }}>
            {features.map(({ icon, title, desc, color }, i) => (
              <div
                key={title}
                className="card"
                style={{
                  cursor: 'default',
                  animation: 'fadeIn 0.5s ease forwards',
                  animationDelay: `${i * 0.08}s`,
                  opacity: 0,
                  border: `1px solid rgba(${color === '#4ade80' ? '74,222,128' : color === '#38bdf8' ? '56,189,248' : color === '#fbbf24' ? '251,191,36' : color === '#a78bfa' ? '167,139,250' : color === '#f472b6' ? '244,114,182' : '52,211,153'},0.2)`,
                }}
              >
                <div style={{
                  width: 56, height: 56,
                  background: `${color}18`,
                  border: `1px solid ${color}40`,
                  borderRadius: 'var(--radius-md)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.7rem', marginBottom: '1.25rem',
                  boxShadow: `0 0 20px ${color}20`,
                }}>
                  {icon}
                </div>
                <h3 style={{ marginBottom: '0.6rem', fontSize: '1.1rem' }}>{title}</h3>
                <p style={{ fontSize: '0.88rem', margin: 0, lineHeight: 1.65 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section style={{
        padding: '6rem 0',
        background: 'linear-gradient(135deg, rgba(22,163,74,0.05) 0%, rgba(14,165,233,0.05) 100%)',
        borderTop: '1px solid var(--border)',
        borderBottom: '1px solid var(--border)',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background image accent */}
        <div style={{
          position: 'absolute', right: 0, top: 0, bottom: 0, width: '45%',
          backgroundImage: 'url(/agriculture.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.08,
          maskImage: 'linear-gradient(to left, rgba(0,0,0,0.8) 0%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to left, rgba(0,0,0,0.8) 0%, transparent 100%)',
        }} />

        <div className="container" style={{ position: 'relative' }}>
          <div style={{ maxWidth: '560px' }}>
            <span className="badge badge-green" style={{ marginBottom: '1rem' }}>How It Works</span>
            <h2 style={{ marginBottom: '1rem', fontWeight: 900 }}>From Field to Forecast in 30 Seconds</h2>
            <p style={{ marginBottom: '3rem' }}>
              No sensors. No field visits. Just your district and season — the AI handles everything else.
            </p>

            {[
              { num: '01', title: 'Select Your Location', desc: 'Pick your Karnataka district and taluk. AI auto-loads your soil chemistry, agro zone and 34-yr rainfall baseline.', icon: '📍' },
              { num: '02', title: 'Choose Your Season', desc: 'Kharif, Rabi or Summer. Add your sowing date for precision GDD-based growth stage timelines.', icon: '📅' },
              { num: '03', title: 'Get AI Recommendations', desc: 'Ranked crop list with suitability scores, yield estimates, growth stages and an irrigation advisory — all explained.', icon: '🌾' },
            ].map(({ num, title, desc, icon }) => (
              <div key={num} style={{ display: 'flex', gap: '1.5rem', marginBottom: '2.5rem' }}>
                <div style={{
                  flexShrink: 0,
                  width: 56, height: 56,
                  background: 'linear-gradient(135deg, rgba(22,163,74,0.2) 0%, rgba(14,165,233,0.2) 100%)',
                  border: '1px solid rgba(74,222,128,0.3)',
                  borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.3rem',
                }}>
                  {icon}
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--green-500)', letterSpacing: '0.15em', marginBottom: '0.35rem' }}>STEP {num}</div>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>{title}</h3>
                  <p style={{ fontSize: '0.9rem', margin: 0 }}>{desc}</p>
                </div>
              </div>
            ))}

            <button
              className="btn btn-primary btn-lg"
              onClick={() => onNavigate('recommend')}
              style={{ marginTop: '1rem' }}
            >
              🌱 Start Now — It's Free
            </button>
          </div>
        </div>
      </section>

      {/* ═══ CTA BANNER ═══ */}
      <section style={{
        padding: '5rem 0',
        position: 'relative',
        overflow: 'hidden',
        background: 'var(--bg-base)',
      }}>
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'url(/agriculture.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center 60%',
          opacity: 0.15,
        }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(135deg, rgba(10,15,13,0.92) 0%, rgba(10,20,15,0.85) 100%)',
        }} />

        <div className="container" style={{ position: 'relative', textAlign: 'center' }}>
          <div style={{
            display: 'inline-block',
            padding: '0.5rem 1.2rem',
            background: 'rgba(74,222,128,0.1)',
            border: '1px solid rgba(74,222,128,0.25)',
            borderRadius: '999px',
            fontSize: '0.85rem',
            color: 'var(--green-400)',
            marginBottom: '1.5rem',
          }}>
            ✨ Free · No account required
          </div>
          <h2 style={{
            fontSize: 'clamp(1.8rem,4vw,3rem)',
            fontWeight: 900,
            marginBottom: '1rem',
            background: 'linear-gradient(135deg, #e8f5e9 0%, #4ade80 60%, #38bdf8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Ready to know what to plant?
          </h2>
          <p style={{ maxWidth: '480px', margin: '0 auto 2.5rem', fontSize: '1.05rem' }}>
            Takes 30 seconds. Just pick your district and season — the AI does the rest.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn btn-primary btn-lg"
              onClick={() => onNavigate('recommend')}
              style={{ boxShadow: '0 8px 40px rgba(22,163,74,0.4)' }}
            >
              🌾 Analyse My Farm
            </button>
            <button
              className="btn btn-secondary btn-lg"
              onClick={() => onNavigate('about')}
            >
              Learn How It Works
            </button>
          </div>
        </div>
      </section>

      {/* Keyframe styles */}
      <style>{`
        @keyframes float-particle {
          0%, 100% { transform: translateY(0px) scale(1); opacity: 0.6; }
          50% { transform: translateY(-20px) scale(1.2); opacity: 1; }
        }
        @keyframes bounce-down {
          0%, 100% { transform: translateX(-50%) translateY(0); }
          50% { transform: translateX(-50%) translateY(8px); }
        }
        .btn-ghost {
          background: transparent;
          border: 1px solid var(--border);
          color: var(--text-secondary);
        }
        .btn-ghost:hover {
          background: rgba(34,197,94,0.07);
          border-color: var(--border-hover);
          color: var(--green-400);
        }
      `}</style>
    </div>
  );
}
