import React, { useState, useEffect } from 'react';
import { useHealth } from '../hooks/useAgrotech';

const NAV_ITEMS = [
  { id: 'home',      label: 'Home',              icon: '🏠' },
  { id: 'recommend', label: 'Get Recommendations', icon: '🌾' },
  { id: 'weather',   label: 'Weather',            icon: '🌦️' },
  { id: 'about',     label: 'About',              icon: 'ℹ️' },
];

export function Navbar({ currentPage, onNavigate }) {
  const health = useHealth();
  const online = health?.status === 'healthy';
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      height: '68px',
      background: scrolled
        ? 'rgba(10,15,13,0.95)'
        : 'rgba(10,15,13,0.6)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      borderBottom: scrolled
        ? '1px solid rgba(74,222,128,0.2)'
        : '1px solid rgba(74,222,128,0.08)',
      transition: 'all 0.3s ease',
      boxShadow: scrolled ? '0 4px 24px rgba(0,0,0,0.4)' : 'none',
      display: 'flex', alignItems: 'center',
    }}>
      <div style={{
        width: '100%', maxWidth: '1200px', margin: '0 auto',
        padding: '0 1.5rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        {/* Logo */}
        <button
          onClick={() => onNavigate('home')}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.6rem',
            background: 'none', border: 'none', cursor: 'pointer', padding: 0,
          }}
        >
          <div style={{
            width: 38, height: 38,
            background: 'linear-gradient(135deg, rgba(22,163,74,0.3) 0%, rgba(14,165,233,0.2) 100%)',
            border: '1px solid rgba(74,222,128,0.35)',
            borderRadius: 'var(--radius-sm)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.3rem',
            boxShadow: '0 0 16px rgba(74,222,128,0.2)',
          }}>🌾</div>
          <div style={{ textAlign: 'left' }}>
            <div style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 800, fontSize: '1.2rem',
              background: 'linear-gradient(135deg, #e8f5e9 0%, #4ade80 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              lineHeight: 1.1,
            }}>
              AgroTech
            </div>
            <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.1em' }}>
              AI Agriculture Intelligence
            </div>
          </div>
        </button>

        {/* Desktop Nav */}
        <ul style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', listStyle: 'none', margin: 0, padding: 0 }}>
          {NAV_ITEMS.map(({ id, label }) => (
            <li key={id}>
              <a
                href="#"
                onClick={e => { e.preventDefault(); onNavigate(id); }}
                style={{
                  display: 'inline-flex', alignItems: 'center',
                  padding: '0.45rem 0.9rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem', fontWeight: currentPage === id ? 700 : 500,
                  color: currentPage === id ? '#4ade80' : 'var(--text-secondary)',
                  background: currentPage === id ? 'rgba(74,222,128,0.1)' : 'transparent',
                  border: currentPage === id ? '1px solid rgba(74,222,128,0.2)' : '1px solid transparent',
                  transition: 'all 0.2s ease',
                  textDecoration: 'none',
                }}
                onMouseEnter={e => { if (currentPage !== id) { e.currentTarget.style.color = '#e8f5e9'; e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; } }}
                onMouseLeave={e => { if (currentPage !== id) { e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.background = 'transparent'; } }}
              >
                {label}
              </a>
            </li>
          ))}
        </ul>

        {/* Status + CTA */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.45rem',
            fontSize: '0.78rem', color: online ? 'var(--green-400)' : '#f87171',
          }}>
            <div style={{
              width: 7, height: 7, borderRadius: '50%',
              background: online ? 'var(--green-400)' : '#ef4444',
              boxShadow: online ? '0 0 8px rgba(74,222,128,0.7)' : '0 0 8px rgba(239,68,68,0.7)',
              animation: online ? 'pulse 2s infinite' : 'none',
            }} />
            <span>{online ? `AI Ready · ${health?.crops_available ?? 0} crops` : 'Connecting…'}</span>
          </div>

          <button
            className="btn btn-primary"
            onClick={() => onNavigate('recommend')}
            style={{
              padding: '0.45rem 1.1rem',
              fontSize: '0.85rem',
              boxShadow: '0 4px 16px rgba(22,163,74,0.35)',
            }}
          >
            🌱 Analyse Farm
          </button>
        </div>
      </div>
    </nav>
  );
}
